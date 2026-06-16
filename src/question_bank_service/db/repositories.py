import json
import sqlite3
from dataclasses import dataclass
from typing import Any

ASSET_PUBLIC_MARKER = "assets/fe-siken/"


class RepositoryError(ValueError):
    """Raised when persisted question bank data is malformed."""


@dataclass(frozen=True)
class Keywords:
    categories: list[str]
    topics: list[str]


@dataclass(frozen=True)
class QuestionCandidate:
    question_id: int
    source_page_label: str
    source_page_url: str
    exam_part: str
    question_no: str
    topic: str
    category: str
    question_url: str
    scraped_at: str


@dataclass(frozen=True)
class Choice:
    label: str
    text: str


@dataclass(frozen=True)
class QuestionDetail:
    question_id: int
    question_url: str
    source_url: str
    question_text: str
    choices: list[Choice]
    answer: str
    explanation: str
    images: list[dict[str, Any]]
    has_images: bool
    fetched_at: str
    learning_explanation: dict[str, Any]
    explanation_ja: str
    distractor_explanations_ja: dict[str, str]
    knowledge_point_ja: str
    exam_point_ja: str
    common_trap_ja: str


class QuestionBankRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def list_keywords(self) -> Keywords:
        categories = self._list_distinct_question_values("category")
        topics = self._list_distinct_question_values("topic")
        return Keywords(categories=categories, topics=topics)

    def find_candidates(
        self,
        *,
        category: str | None = None,
        categories: list[str] | None = None,
        topic: str | None = None,
        url: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[QuestionCandidate]:
        clauses = ["exam_part = ?"]
        params: list[Any] = ["科目A"]

        if category:
            clauses.append("category = ?")
            params.append(category)
        if categories:
            placeholders = ", ".join("?" for _ in categories)
            clauses.append(f"category IN ({placeholders})")
            params.extend(categories)
        if topic:
            clauses.append("topic = ?")
            params.append(topic)
        if url:
            clauses.append("url = ?")
            params.append(url)

        params.extend([limit, offset])
        rows = self._connection.execute(
            f"""
            SELECT
                id, source_page_label, source_page_url, exam_part, question_no,
                topic, category, url, scraped_at
            FROM questions
            WHERE {' AND '.join(clauses)}
            ORDER BY id
            LIMIT ? OFFSET ?
            """,
            params,
        ).fetchall()
        return [_candidate_from_row(row) for row in rows]

    def get_detail_by_url(self, question_url: str) -> QuestionDetail | None:
        row = self._detail_query("q.url = ?", [question_url])
        return _detail_from_row(row) if row is not None else None

    def get_detail_by_id(self, question_id: int) -> QuestionDetail | None:
        row = self._detail_query("q.id = ?", [question_id])
        return _detail_from_row(row) if row is not None else None

    def get_details_by_urls(self, question_urls: list[str]) -> list[QuestionDetail]:
        details_by_url = {
            detail.question_url: detail
            for detail in (self.get_detail_by_url(question_url) for question_url in question_urls)
            if detail is not None
        }
        return [details_by_url[url] for url in question_urls if url in details_by_url]

    def _list_distinct_question_values(self, column: str) -> list[str]:
        rows = self._connection.execute(
            f"""
            SELECT DISTINCT {column}
            FROM questions
            WHERE exam_part = ? AND {column} != ''
            ORDER BY {column}
            """,
            ["科目A"],
        ).fetchall()
        return [row[0] for row in rows]

    def _detail_query(self, where_clause: str, params: list[Any]) -> sqlite3.Row | None:
        learning_columns = self._learning_detail_select_columns()
        return self._connection.execute(
            f"""
            SELECT
                q.id AS question_id,
                q.url AS question_url,
                d.question_text,
                d.choices_json,
                d.answer,
                d.explanation,
                d.images_json,
                d.has_images,
                d.fetched_at,
                {learning_columns}
            FROM questions q
            JOIN question_details d ON q.url = d.question_url
            WHERE {where_clause}
            """,
            params,
        ).fetchone()

    def _learning_detail_select_columns(self) -> str:
        columns = {
            row["name"]
            for row in self._connection.execute("PRAGMA table_info(question_details)").fetchall()
        }
        select_columns = []
        defaults = {
            "learning_explanation_json": "'{}'",
            "explanation_ja": "''",
            "distractor_explanations_ja_json": "'{}'",
            "knowledge_point_ja": "''",
            "exam_point_ja": "''",
            "common_trap_ja": "''",
        }
        for column, default in defaults.items():
            expression = f"d.{column}" if column in columns else default
            select_columns.append(f"{expression} AS {column}")
        return ",\n                ".join(select_columns)


def _candidate_from_row(row: sqlite3.Row) -> QuestionCandidate:
    return QuestionCandidate(
        question_id=row["id"],
        source_page_label=row["source_page_label"],
        source_page_url=row["source_page_url"],
        exam_part=row["exam_part"],
        question_no=row["question_no"],
        topic=row["topic"],
        category=row["category"],
        question_url=row["url"],
        scraped_at=row["scraped_at"],
    )


def _detail_from_row(row: sqlite3.Row) -> QuestionDetail:
    return QuestionDetail(
        question_id=row["question_id"],
        question_url=row["question_url"],
        source_url=row["question_url"],
        question_text=row["question_text"],
        choices=_parse_choices(row["choices_json"]),
        answer=row["answer"],
        explanation=row["explanation"],
        images=_parse_images(row["images_json"]),
        has_images=bool(row["has_images"]),
        fetched_at=row["fetched_at"],
        learning_explanation=_parse_optional_object(row["learning_explanation_json"]),
        explanation_ja=row["explanation_ja"],
        distractor_explanations_ja=_parse_string_dict(row["distractor_explanations_ja_json"]),
        knowledge_point_ja=row["knowledge_point_ja"],
        exam_point_ja=row["exam_point_ja"],
        common_trap_ja=row["common_trap_ja"],
    )


def _parse_choices(value: str) -> list[Choice]:
    raw_choices = _parse_json(value, field_name="choices_json", expected_type=(list, dict))
    if isinstance(raw_choices, dict):
        return [
            Choice(label=label, text=text)
            for label, text in raw_choices.items()
            if isinstance(label, str) and isinstance(text, str)
        ]

    choices: list[Choice] = []
    for item in raw_choices:
        if not isinstance(item, dict) or not isinstance(item.get("label"), str):
            raise RepositoryError("Invalid choices_json: each choice requires a label")
        if not isinstance(item.get("text"), str):
            raise RepositoryError("Invalid choices_json: each choice requires text")
        choices.append(Choice(label=item["label"], text=item["text"]))
    return choices


def _parse_images(value: str) -> list[dict[str, Any]]:
    raw_images = _parse_json(value, field_name="images_json", expected_type=list)
    normalized_images: list[dict[str, Any]] = []
    for item in raw_images:
        if not isinstance(item, dict):
            raise RepositoryError("Invalid images_json: each image requires an object")
        normalized_images.append(_normalize_image_metadata(item))
    return normalized_images


def _normalize_image_metadata(item: dict[str, Any]) -> dict[str, Any]:
    public_path = item.get("publicPath") or item.get("public_path")
    if not isinstance(public_path, str) or not public_path.strip():
        local_path = item.get("localPath") or item.get("local_path")
        public_path = _public_path_from_local_path(local_path)

    normalized: dict[str, Any] = {}
    if isinstance(public_path, str) and public_path.strip():
        normalized["publicPath"] = _normalize_public_asset_path(public_path)

    for key, value in item.items():
        if key in {"publicPath", "public_path", "localPath", "local_path"}:
            continue
        normalized[key] = value

    return normalized


def _public_path_from_local_path(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.replace("\\", "/")
    marker_index = normalized.find(ASSET_PUBLIC_MARKER)
    if marker_index != -1:
        return normalized[marker_index:]

    file_name = normalized.rstrip("/").rsplit("/", maxsplit=1)[-1]
    return file_name or None


def _normalize_public_asset_path(value: str) -> str:
    normalized = value.replace("\\", "/").strip()
    marker_index = normalized.find(ASSET_PUBLIC_MARKER)
    if marker_index != -1:
        normalized = normalized[marker_index:]
        return f"/{normalized.lstrip('/')}"

    normalized = normalized.lstrip("/")
    if normalized.startswith("assets/"):
        normalized = normalized.removeprefix("assets/")
    return f"/{ASSET_PUBLIC_MARKER}{normalized}"


def _parse_json(value: str, *, field_name: str, expected_type: type | tuple[type, ...]) -> Any:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise RepositoryError(f"Invalid {field_name}: {exc.msg}") from exc

    if not isinstance(parsed, expected_type):
        expected_name = (
            " or ".join(item.__name__ for item in expected_type)
            if isinstance(expected_type, tuple)
            else expected_type.__name__
        )
        raise RepositoryError(f"Invalid {field_name}: expected {expected_name}")
    return parsed


def _parse_optional_object(value: str) -> dict[str, Any]:
    if not value or value == "{}":
        return {}
    parsed = _parse_json(value, field_name="learning_explanation_json", expected_type=dict)
    return parsed


def _parse_string_dict(value: str) -> dict[str, str]:
    if not value or value == "{}":
        return {}
    parsed = _parse_json(value, field_name="distractor_explanations_ja_json", expected_type=dict)
    return {str(key): str(item) for key, item in parsed.items()}
