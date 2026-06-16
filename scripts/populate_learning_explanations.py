from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DB_PATH = Path("data/fe_siken_questions.sqlite")
MAPPINGS_PATH = Path("data/question_topic_mappings.json")

LEARNING_COLUMNS = {
    "learning_explanation_json": "TEXT NOT NULL DEFAULT '{}'",
    "explanation_ja": "TEXT NOT NULL DEFAULT ''",
    "distractor_explanations_ja_json": "TEXT NOT NULL DEFAULT '{}'",
    "knowledge_point_ja": "TEXT NOT NULL DEFAULT ''",
    "exam_point_ja": "TEXT NOT NULL DEFAULT ''",
    "common_trap_ja": "TEXT NOT NULL DEFAULT ''",
    "learning_explanation_generated_at": "TEXT NOT NULL DEFAULT ''",
    "learning_explanation_source": "TEXT NOT NULL DEFAULT ''",
}


def main() -> None:
    mappings_by_url = _load_mappings(MAPPINGS_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _ensure_columns(conn)

    generated_at = datetime.now(UTC).isoformat()
    rows = conn.execute(
        """
        SELECT
            q.url,
            q.exam_part,
            q.category,
            q.topic,
            d.question_text,
            d.choices_json,
            d.answer,
            d.explanation,
            d.images_json,
            d.has_images
        FROM questions q
        JOIN question_details d ON q.url = d.question_url
        WHERE q.exam_part = '科目A'
        ORDER BY q.id
        """
    ).fetchall()

    for row in rows:
        payload = build_learning_explanation(
            question_url=row["url"],
            exam_part=row["exam_part"],
            category=row["category"],
            topic=row["topic"],
            question_text=row["question_text"],
            choices_json=row["choices_json"],
            answer=row["answer"],
            existing_explanation=row["explanation"],
            has_images=bool(row["has_images"]),
            mapping=mappings_by_url.get(row["url"], {}),
        )
        conn.execute(
            """
            UPDATE question_details
            SET
                learning_explanation_json = ?,
                explanation_ja = ?,
                distractor_explanations_ja_json = ?,
                knowledge_point_ja = ?,
                exam_point_ja = ?,
                common_trap_ja = ?,
                learning_explanation_generated_at = ?,
                learning_explanation_source = ?
            WHERE question_url = ?
            """,
            (
                json.dumps(payload, ensure_ascii=False),
                payload["explanationJa"],
                json.dumps(payload["distractorExplanationsJa"], ensure_ascii=False),
                payload["knowledgePointJa"],
                payload["examPointJa"],
                payload["commonTrapJa"],
                generated_at,
                "deterministic_existing_explanation_v1",
                row["url"],
            ),
        )
    conn.commit()
    print(json.dumps({"updated": len(rows), "generatedAt": generated_at}, ensure_ascii=False))
    conn.close()


def build_learning_explanation(
    *,
    question_url: str,
    exam_part: str,
    category: str,
    topic: str,
    question_text: str,
    choices_json: str,
    answer: str,
    existing_explanation: str,
    has_images: bool,
    mapping: dict[str, Any],
) -> dict[str, Any]:
    choices = _parse_choices(choices_json)
    explanation = _short_explanation(existing_explanation)
    if has_images:
        explanation = (
            f"{explanation} "
            "図表が示されている問題では、図中の条件や対応関係を問題文と照合して判断します。"
        )

    topic_tags = mapping.get("topicTags") if isinstance(mapping.get("topicTags"), list) else []
    syllabus_area = (
        mapping.get("syllabusArea") if isinstance(mapping.get("syllabusArea"), str) else ""
    )
    distractors = {
        choice["label"]: _distractor_text(
            label=choice["label"],
            text=choice["text"],
            answer=answer,
            topic=topic,
            category=category,
        )
        for choice in choices
        if choice["label"] != answer
    }

    exam_hint = (
        f"「{category}」分野の問題として、"
        f"問題文が問う条件と選択肢の記述が「{topic}」に合うかを確認します。"
    )
    if syllabus_area:
        exam_hint += f" 大分類は「{syllabus_area}」として扱います。"
    if topic_tags:
        exam_hint += f" 関連タグは「{', '.join(str(tag) for tag in topic_tags)}」です。"

    return {
        "questionUrl": question_url,
        "explanationJa": explanation,
        "distractorExplanationsJa": distractors,
        "knowledgePointJa": topic,
        "examPointJa": exam_hint,
        "commonTrapJa": (
            "用語名や選択肢の表現だけで即断せず、問題文の条件、正答の根拠、"
            "既存解説で確認できる範囲を照合する点に注意します。"
        ),
        "sourceExamPart": exam_part,
        "sourceQuestionTextHash": hashlib.sha1(question_text.encode("utf-8")).hexdigest(),
    }


def _ensure_columns(conn: sqlite3.Connection) -> None:
    existing = {row[1] for row in conn.execute("PRAGMA table_info(question_details)")}
    for column, ddl in LEARNING_COLUMNS.items():
        if column not in existing:
            conn.execute(f"ALTER TABLE question_details ADD COLUMN {column} {ddl}")


def _load_mappings(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    mappings = data.get("mappings", [])
    if not isinstance(mappings, list):
        return {}
    return {
        item["questionUrl"]: item
        for item in mappings
        if isinstance(item, dict) and isinstance(item.get("questionUrl"), str)
    }


def _parse_choices(value: str) -> list[dict[str, str]]:
    parsed = json.loads(value)
    if isinstance(parsed, dict):
        return [
            {"label": str(label), "text": str(text)}
            for label, text in parsed.items()
        ]
    if isinstance(parsed, list):
        return [
            {"label": str(item.get("label", "")), "text": str(item.get("text", ""))}
            for item in parsed
            if isinstance(item, dict)
        ]
    return []


def _short_explanation(value: str) -> str:
    value = _sanitize_explanation_text(value)
    sentences = []
    for sentence in value.replace("\r\n", "\n").split("。"):
        stripped = sentence.strip()
        if stripped:
            sentences.append(f"{stripped}。")
        if len(sentences) == 5:
            break
    if sentences:
        return "".join(sentences)
    return "既存の問題文、選択肢、正答から確認できる範囲で、正答に対応する記述を選びます。"


def _sanitize_explanation_text(value: str) -> str:
    sanitized = re.sub(r"!\[[^\]]*]\([^)]+\)", "", value)
    sanitized = re.sub(r"\b[A-Za-z]:[\\/][^\s。]+", "", sanitized)
    sanitized = re.sub(r"/(?:app|assets)/[^\s。]+", "", sanitized)
    return sanitized


def _distractor_text(
    *,
    label: str,
    text: str,
    answer: str,
    topic: str,
    category: str,
) -> str:
    choice_text = _sanitize_explanation_text(text).strip() or "画像選択肢"
    return (
        f"選択肢{label}「{choice_text}」は正答の選択肢{answer}ではありません。"
        f"この問題は「{category}」の「{topic}」を問うため、問題文の条件と既存解説の根拠に合うかを確認します。"
    )


if __name__ == "__main__":
    main()
