# ruff: noqa: E501

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DB_PATH = Path("data/fe_siken_questions.sqlite")

AREAS: dict[str, dict[str, Any]] = {
    "mathematics": {
        "display": "基礎理論・数学",
        "aliases": ["math", "theory"],
    },
    "computer_system": {
        "display": "コンピュータシステム",
        "aliases": ["computer system", "hardware", "operating system"],
    },
    "software_design": {
        "display": "ソフトウェア・開発",
        "aliases": ["software design", "development", "algorithm"],
    },
    "database": {
        "display": "データベース",
        "aliases": ["database", "sql"],
    },
    "network": {
        "display": "ネットワーク",
        "aliases": ["network", "tcp/ip"],
    },
    "security": {
        "display": "情報セキュリティ",
        "aliases": ["security"],
    },
    "project_management": {
        "display": "プロジェクトマネジメント",
        "aliases": ["project management"],
    },
    "service_management": {
        "display": "サービスマネジメント",
        "aliases": ["service management", "itil"],
    },
    "strategy": {
        "display": "ストラテジ系",
        "aliases": ["strategy", "business"],
    },
    "business_law": {
        "display": "法務・標準化",
        "aliases": ["law", "standardization"],
    },
    "management": {
        "display": "マネジメント系",
        "aliases": ["management", "audit"],
    },
    "technology": {
        "display": "テクノロジ系",
        "aliases": ["technology"],
    },
}

CATEGORY_AREA: dict[str, str] = {
    "UX/UIデザイン": "software_design",
    "e-ビジネス": "strategy",
    "その他の法律・ガイドライン": "business_law",
    "その他の言語": "software_design",
    "アルゴリズム": "software_design",
    "エンジニアリングシステム": "computer_system",
    "オペレーティングシステム": "computer_system",
    "オープンソースソフトウェア": "software_design",
    "サービスの設計・移行": "service_management",
    "サービスの運用": "service_management",
    "サービスマネジメント": "service_management",
    "サービスマネジメントプロセス": "service_management",
    "システムの構成": "computer_system",
    "システムの評価指標": "computer_system",
    "システム化計画": "strategy",
    "システム活用促進・評価": "management",
    "システム監査": "management",
    "システム結合・適格性テスト": "software_design",
    "システム要件定義": "software_design",
    "セキュリティ実装技術": "security",
    "セキュリティ技術評価": "security",
    "セキュリティ関連法規": "business_law",
    "ソフトウェア方式設計・詳細設計": "software_design",
    "ソフトウェア構築": "software_design",
    "ソフトウェア結合・適格性テスト": "software_design",
    "ソフトウェア要件定義": "software_design",
    "ソリューションビジネス": "strategy",
    "データベース応用": "database",
    "データベース方式": "database",
    "データベース設計": "database",
    "データ操作": "database",
    "データ構造": "software_design",
    "データ構造及びアルゴリズム": "software_design",
    "データ通信と制御": "network",
    "トランザクション処理": "database",
    "ネットワーク応用": "network",
    "ネットワーク方式": "network",
    "ネットワーク管理": "network",
    "ハードウェア": "computer_system",
    "バス": "computer_system",
    "ビジネスシステム": "strategy",
    "ビジネス戦略と目標・評価": "strategy",
    "ファイルシステム": "computer_system",
    "ファシリティマネジメント": "service_management",
    "プログラミング": "software_design",
    "プログラミングの諸分野への適用": "software_design",
    "プログラムの基本要素": "software_design",
    "プログラム言語": "software_design",
    "プロジェクトのコスト": "project_management",
    "プロジェクトのコミュニケーション": "project_management",
    "プロジェクトのスコープ": "project_management",
    "プロジェクトのステークホルダ": "project_management",
    "プロジェクトのリスク": "project_management",
    "プロジェクトの品質": "project_management",
    "プロジェクトの時間": "project_management",
    "プロジェクトの統合": "project_management",
    "プロジェクトの資源": "project_management",
    "プロジェクトマネジメント": "project_management",
    "プロセッサ": "computer_system",
    "マルチメディア応用": "computer_system",
    "マルチメディア技術": "computer_system",
    "マーケティング": "strategy",
    "ミドルウェア": "computer_system",
    "メモリ": "computer_system",
    "ユーザーインタフェース技術": "software_design",
    "会計・財務": "strategy",
    "保守・廃棄": "management",
    "入出力デバイス": "computer_system",
    "入出力装置": "computer_system",
    "内部統制": "management",
    "労働関連・取引関連法規": "business_law",
    "受入れ支援": "management",
    "応用数学": "mathematics",
    "情報に関する理論": "mathematics",
    "情報システム戦略": "strategy",
    "情報セキュリティ": "security",
    "情報セキュリティ対策": "security",
    "情報セキュリティ管理": "security",
    "技術開発戦略の立案": "strategy",
    "技術開発計画": "strategy",
    "業務プロセス": "strategy",
    "業務分析・データ利活用": "strategy",
    "構成管理・変更管理": "management",
    "標準化関連": "business_law",
    "民生機器": "strategy",
    "産業機器": "strategy",
    "知的財産権": "business_law",
    "知的財産適用管理": "business_law",
    "経営・組織論": "strategy",
    "経営戦略手法": "strategy",
    "経営管理システム": "strategy",
    "要件定義": "software_design",
    "計測・制御に関する理論": "mathematics",
    "調達計画・実施": "management",
    "通信に関する理論": "network",
    "通信プロトコル": "network",
    "開発ツール": "software_design",
    "開発プロセス・手法": "software_design",
    "開発環境管理": "software_design",
    "離散数学": "mathematics",
}

EN_ALIASES = {
    "データ操作": ["sql", "select", "join", "group by", "having"],
    "トランザクション処理": ["transaction", "commit", "rollback", "lock", "acid"],
    "データベース設計": ["database design", "normalization", "er diagram"],
    "情報セキュリティ": ["security", "risk", "threat"],
    "情報セキュリティ対策": ["security controls", "malware", "waf"],
    "セキュリティ実装技術": ["encryption", "authentication", "tls", "https"],
    "通信プロトコル": ["network protocol", "tcp/ip", "dns", "http"],
    "ネットワーク方式": ["network architecture", "lan", "wan", "ip"],
    "アルゴリズム": ["algorithm", "complexity"],
    "データ構造": ["data structure", "tree", "list", "queue", "stack"],
    "離散数学": ["discrete mathematics", "logic", "set"],
    "応用数学": ["applied mathematics", "statistics", "probability"],
    "オペレーティングシステム": ["operating system", "os", "process"],
    "メモリ": ["memory", "cache", "dram"],
    "プロセッサ": ["processor", "cpu"],
    "システムの評価指標": ["availability", "mtbf", "mttr", "performance"],
}

CANONICAL_TOPIC_IDS = {
    "トランザクション処理": "transaction",
    "データ操作": "sql",
    "情報セキュリティ": "security",
    "通信プロトコル": "network",
    "アルゴリズム": "algorithm",
    "システムの評価指標": "availability",
}

TERM_ALIASES = [
    ("sql", ["SQL", "SELECT", "GROUP BY", "HAVING", "JOIN", "射影", "結合"]),
    ("transaction", ["トランザクション", "コミット", "ロールバック", "ACID", "排他制御", "ロック"]),
    ("security", ["セキュリティ", "暗号", "認証", "マルウェア", "脆弱性", "WAF", "TLS", "HTTPS"]),
    ("network", ["TCP", "IP", "DNS", "HTTP", "LAN", "ルータ", "スイッチ", "プロトコル"]),
    ("algorithm", ["アルゴリズム", "探索", "整列", "計算量", "オーダー"]),
    ("availability", ["稼働率", "MTBF", "MTTR", "可用性"]),
    ("normalization", ["正規化", "関数従属", "第3正規形", "E-R"]),
]


def stable_id(prefix: str, text: str) -> str:
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}_{digest}"


def topic_tag_id(category: str) -> str:
    return CANONICAL_TOPIC_IDS.get(category, stable_id("topic", category))


def snippet(text: str | None, limit: int = 140) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()[:limit]


def aliases_for(text: str) -> list[str]:
    return sorted({alias for alias, terms in TERM_ALIASES if any(term in text for term in terms)})


def load_rows() -> list[sqlite3.Row]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn.execute(
        """
        SELECT
          q.id, q.source_page_label, q.source_page_url, q.exam_part, q.question_no,
          q.topic, q.category, q.url, q.scraped_at,
          d.question_text, d.choices_json, d.answer, d.explanation, d.images_json,
          d.has_images, d.fetched_at
        FROM questions q
        LEFT JOIN question_details d ON q.url = d.question_url
        ORDER BY q.id
        """
    ).fetchall()


def main() -> None:
    rows = load_rows()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    generated_at = datetime.now(UTC).isoformat()

    tags: list[dict[str, Any]] = []
    for area_id, meta in AREAS.items():
        tags.append(
            {
                "id": area_id,
                "level": "syllabusArea",
                "displayNameJa": meta["display"],
                "displayNameEn": area_id.replace("_", " ").title(),
                "aliasesJa": [meta["display"]],
                "aliasesEn": meta["aliases"],
                "parentId": None,
                "syllabusArea": area_id,
            }
        )

    category_ids: dict[str, str] = {}
    for category in sorted({row["category"] for row in rows if row["category"]}):
        area = CATEGORY_AREA.get(category, "technology")
        category_id = topic_tag_id(category)
        category_ids[category] = category_id
        tags.append(
            {
                "id": category_id,
                "level": "topicTag",
                "displayNameJa": category,
                "displayNameEn": category,
                "aliasesJa": [category],
                "aliasesEn": sorted(set(EN_ALIASES.get(category, []) + aliases_for(category))),
                "parentId": area,
                "syllabusArea": area,
            }
        )

    topic_ids = {topic: stable_id("kp", topic) for topic in sorted({r["topic"] for r in rows if r["topic"]})}
    topic_category_counter: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        if row["topic"] and row["category"]:
            topic_category_counter[row["topic"]][row["category"]] += 1

    for topic, topic_id in topic_ids.items():
        parent_category = topic_category_counter[topic].most_common(1)[0][0]
        parent_id = category_ids[parent_category]
        area = CATEGORY_AREA.get(parent_category, "technology")
        tags.append(
            {
                "id": topic_id,
                "level": "knowledgePoint",
                "displayNameJa": topic,
                "displayNameEn": topic,
                "aliasesJa": [topic],
                "aliasesEn": aliases_for(topic),
                "parentId": parent_id,
                "syllabusArea": area,
            }
        )

    mappings: list[dict[str, Any]] = []
    area_stats: Counter[str] = Counter()
    topic_stats: Counter[str] = Counter()
    low_confidence: list[dict[str, Any]] = []
    missing_details = 0
    fallback_categories = set()

    for row in rows:
        category = row["category"] or ""
        topic = row["topic"] or ""
        area = CATEGORY_AREA.get(category, "technology")
        if category and category not in CATEGORY_AREA:
            fallback_categories.add(category)
        category_id = category_ids.get(category)
        topic_id = topic_ids.get(topic)
        has_detail = row["question_text"] is not None
        if not has_detail:
            missing_details += 1
        confidence = 0.94 if has_detail and category in CATEGORY_AREA else 0.70
        needs_review = confidence < 0.75
        if needs_review:
            low_confidence.append(dict(row))

        images = []
        try:
            images = json.loads(row["images_json"]) if row["images_json"] else []
        except json.JSONDecodeError:
            images = []
        image_public_paths = []
        for image in images if isinstance(images, list) else []:
            if isinstance(image, dict):
                path = image.get("publicPath") or image.get("public_path") or image.get("url")
                if isinstance(path, str):
                    image_public_paths.append(path)

        evidence = [
            {"field": "existingCategory", "text": category, "matchedTerms": [category]},
            {"field": "existingTopic", "text": topic, "matchedTerms": [topic]},
        ]
        if row["question_text"]:
            evidence.append(
                {
                    "field": "questionText",
                    "text": snippet(row["question_text"]),
                    "matchedTerms": [term for term in [category, topic] if term and term in row["question_text"]],
                }
            )
        if row["explanation"]:
            evidence.append(
                {
                    "field": "explanation",
                    "text": snippet(row["explanation"]),
                    "matchedTerms": [term for term in [category, topic] if term and term in row["explanation"]],
                }
            )

        area_stats[area] += 1
        if category_id:
            topic_stats[category_id] += 1

        mappings.append(
            {
                "questionId": row["id"],
                "questionUrl": row["url"],
                "sourcePageLabel": row["source_page_label"],
                "examPart": row["exam_part"],
                "questionNo": row["question_no"],
                "primaryTag": topic_id or category_id or area,
                "topicTags": [category_id] if category_id else [],
                "knowledgePoints": [topic_id] if topic_id else [],
                "syllabusArea": area,
                "existingCategory": category,
                "existingTopic": topic,
                "hasImages": bool(row["has_images"]) if row["has_images"] is not None else False,
                "imagePublicPaths": image_public_paths,
                "matchedEvidence": evidence,
                "confidence": confidence,
                "needsHumanReview": needs_review,
            }
        )

    def urls_for_category(category: str, limit: int = 5) -> list[str]:
        return [
            mapping["questionUrl"]
            for mapping in mappings
            if mapping["examPart"] == "科目A" and mapping["existingCategory"] == category
        ][:limit]

    fixtures = []
    for query_name, category in [
        ("transaction", "トランザクション処理"),
        ("sql", "データ操作"),
        ("security", "情報セキュリティ"),
        ("network_protocol", "通信プロトコル"),
        ("algorithm", "アルゴリズム"),
    ]:
        urls = urls_for_category(category)
        fixtures.append(
            {
                "query": {
                    "examPart": "科目A",
                    "keywords": [category],
                    "topicTags": [category_ids[category]],
                    "limit": min(5, len(urls)),
                },
                "expectedAnyQuestionUrls": urls,
                "mustNotReturnDefaultUnmatchedQuestions": True,
                "notes": f"{query_name} fixture generated from existing category {category}.",
            }
        )
    fixtures.append(
        {
            "query": {"examPart": "科目A", "keywords": ["__NO_SUCH_FE_TOPIC__"], "limit": 5},
            "expectedAnyQuestionUrls": [],
            "mustReturnShortage": True,
            "mustNotReturnDefaultUnmatchedQuestions": True,
        }
    )

    Path("data/question_keyword_taxonomy.json").write_text(
        json.dumps(
            {
                "version": 1,
                "language": "ja",
                "generatedAt": generated_at,
                "sourceDatabase": DB_PATH.as_posix(),
                "legacyTagMappings": [
                    {
                        "legacyId": stable_id("topic", category),
                        "canonicalId": canonical_id,
                        "reason": "high-traffic topic used by daily study selection",
                    }
                    for category, canonical_id in CANONICAL_TOPIC_IDS.items()
                ],
                "tags": tags,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    Path("data/question_topic_mappings.json").write_text(
        json.dumps(
            {
                "version": 1,
                "language": "ja",
                "generatedAt": generated_at,
                "sourceDatabase": DB_PATH.as_posix(),
                "mappings": mappings,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    Path("data/question_keyword_search_fixtures.json").write_text(
        json.dumps(
            {
                "version": 1,
                "language": "ja",
                "generatedAt": generated_at,
                "fixtures": fixtures,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    area_lines = [
        f"| `{area}` | {AREAS[area]['display']} | {count} |"
        for area, count in area_stats.most_common()
    ]
    tag_by_id = {tag["id"]: tag for tag in tags}
    topic_lines = [
        f"| `{tag_id}` | {tag_by_id[tag_id]['displayNameJa']} | `{tag_by_id[tag_id]['syllabusArea']}` | {count} |"
        for tag_id, count in topic_stats.most_common(50)
    ]
    review_lines = [
        f"- `0.70` {row['exam_part']} {row['question_no']} {row['category']} / {row['topic']} - {row['url']}"
        for row in low_confidence[:30]
    ]
    exam_part_lines = [
        f"| {row['exam_part']} | {row['c']} |"
        for row in conn.execute(
            "select exam_part, count(*) c from questions group by exam_part order by exam_part"
        )
    ]

    Path("docs/question-keyword-taxonomy.md").write_text(
        f"""# Question Keyword Taxonomy

## Purpose

This taxonomy lets the FE Question Bank Runtime expose stable searchable learning topics to consumer applications. Japanese question text, choices, explanations, and existing category/topic values are kept in Japanese and are not translated back into source data.

## Three-Level Model

| Level | Purpose | Source |
| --- | --- | --- |
| `syllabusArea` | Coarse filtering by exam syllabus area | Rule mapping from existing `questions.category` |
| `topicTag` | Main searchable topic used by daily practice plans | Existing `questions.category` |
| `knowledgePoint` | Specific review point for a question | Existing `questions.topic` |

## Naming Rules

- IDs are stable lowercase identifiers.
- `syllabusArea` uses fixed readable IDs such as `database` and `security`.
- `topicTag` and `knowledgePoint` use stable SHA-1 based IDs because the source labels are Japanese.
- Japanese source labels are preserved in `displayNameJa` and `aliasesJa`.
- English abbreviations such as SQL, ACID, TLS, and MTBF are stored in `aliasesEn` when detectable.

## Syllabus Areas

| syllabusArea | displayNameJa | questionCount |
| --- | --- | ---: |
{chr(10).join(area_lines)}

## Top TopicTags

| id | displayNameJa | syllabusArea | questionCount |
| --- | --- | --- | ---: |
{chr(10).join(topic_lines)}

## Runtime Search Example

```json
{{
  "examPart": "科目A",
  "topicTags": ["{category_ids['トランザクション処理']}"],
  "limit": 5
}}
```

Runtime should resolve `topicTags`, `knowledgePoints`, and `syllabusArea` through `data/question_topic_mappings.json` and return only matched question URLs. Unknown keywords must return an explicit shortage response, not default ordered questions.

## Maintenance Rules

1. Regenerate the JSON files after updating `questions.category` or `questions.topic`.
2. Review low-confidence mappings listed in `docs/question-keyword-generation-report.md`.
3. Keep original Japanese question content unchanged.
4. Keep browser image paths as public paths only; do not expose host filesystem paths to consumers.
""",
        encoding="utf-8",
    )

    notes = []
    if missing_details:
        notes.append(
            f"- `question_details` is missing for {missing_details} questions. These mappings are generated from existing category/topic only and require review."
        )
    if fallback_categories:
        notes.append(
            f"- {len(fallback_categories)} categories fell back to `technology`: {', '.join(sorted(fallback_categories))}"
        )
    if not notes:
        notes.append("- No major schema-level data quality issue was detected for keyword generation.")

    readable_topic_count = sum(
        1 for tag in tags if tag["level"] == "topicTag" and not tag["id"].startswith("topic_")
    )
    hash_topic_count = sum(
        1 for tag in tags if tag["level"] == "topicTag" and tag["id"].startswith("topic_")
    )

    Path("docs/question-keyword-generation-report.md").write_text(
        f"""# Question Keyword Generation Report

## Data Source

- SQLite: `data/fe_siken_questions.sqlite`
- Generated at: `{generated_at}`
- Read model: `questions` LEFT JOIN `question_details`

## Tables and Fields Read

| Table | Fields |
| --- | --- |
| `questions` | `id`, `source_page_label`, `source_page_url`, `exam_part`, `question_no`, `topic`, `category`, `url`, `scraped_at` |
| `question_details` | `question_url`, `question_text`, `choices_json`, `answer`, `explanation`, `images_json`, `has_images`, `fetched_at` |
| `question_assets` | `question_url`, `section`, `choice_label`, `asset_type`, `url`, `alt`, `width`, `height`, `local_path`, `public_path` |

## Summary

| Metric | Count |
| --- | ---: |
| questions total | {len(rows)} |
| question_details joined | {sum(1 for row in rows if row['question_text'] is not None)} |
| question_assets rows | {conn.execute('select count(*) from question_assets').fetchone()[0]} |
| mappings generated | {len(mappings)} |
| tags generated | {len(tags)} |
| low-confidence / review required mappings | {len(low_confidence)} |
| missing detail rows | {missing_details} |
| fallback categories | {len(fallback_categories)} |
| readable canonical topicTag IDs | {readable_topic_count} |
| hash-based topicTag IDs | {hash_topic_count} |

## Exam Part Counts

| examPart | Count |
| --- | ---: |
{chr(10).join(exam_part_lines)}

## SyllabusArea Counts

| syllabusArea | displayNameJa | questionCount |
| --- | --- | ---: |
{chr(10).join(area_lines)}

## Top TopicTag Counts

| topicTag | displayNameJa | syllabusArea | questionCount |
| --- | --- | --- | ---: |
{chr(10).join(topic_lines)}

## Human Review Samples

{chr(10).join(review_lines) if review_lines else "- None."}

## Data Quality Notes

{chr(10).join(notes)}
- The generated topic and knowledge-point IDs are stable but hash-based. If these IDs become public API contracts, consider replacing high-traffic tags with curated human-readable IDs in a controlled migration.
- `question_assets` metadata exists, but this report does not verify that every referenced image file exists under `QUESTION_ASSET_ROOT`.

## High-Frequency Canonical ID Migration

| legacyId | canonicalId | source category |
| --- | --- | --- |
{chr(10).join(f"| `{stable_id('topic', category)}` | `{canonical_id}` | {category} |" for category, canonical_id in CANONICAL_TOPIC_IDS.items())}

## Runtime API Implementation Status

1. `GET /keywords` returns `version`, `language`, and `tags` from `data/question_keyword_taxonomy.json`.
2. `POST /questions/candidates/search` accepts `keywords`, `topicTags`, `knowledgePoints`, and `syllabusArea`, then filters through `data/question_topic_mappings.json`.
3. Unknown or underfilled searches return explicit `shortage.reason` instead of default ordered questions.
4. `POST /questions/details/batch` items include `primaryTag`, `topicTags`, `knowledgePoints`, and `syllabusArea` when mappings exist.

## Generated Files

- `docs/question-keyword-taxonomy.md`
- `docs/question-keyword-generation-report.md`
- `data/question_keyword_taxonomy.json`
- `data/question_topic_mappings.json`
- `data/question_keyword_search_fixtures.json`

## Verification Plan

- Parse all generated JSON files as UTF-8 JSON.
- Assert `questions` count equals `mappings` count.
- Assert transaction / sql / security / network / algorithm fixtures have expected URLs.
- After Runtime implementation, add contract tests for unknown keywords returning shortage without default questions.
""",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "questions": len(rows),
                "details": sum(1 for row in rows if row["question_text"] is not None),
                "tags": len(tags),
                "mappings": len(mappings),
                "lowConfidence": len(low_confidence),
                "missingDetails": missing_details,
                "fallbackCategories": len(fallback_categories),
                "fixtures": len(fixtures),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
