import json
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from question_bank_service.app import create_app
from question_bank_service.config import Settings


def test_runtime_api_exposes_read_only_question_bank(tmp_path: Path) -> None:
    db_path = _create_runtime_db(tmp_path)
    client = TestClient(create_app(settings=_settings(db_path, _create_keyword_files(tmp_path))))

    assert client.get("/health").json() == {
        "ok": True,
        "database": "ready",
        "readOnly": True,
    }

    keywords = client.get("/keywords").json()
    assert keywords["version"] == 1
    assert keywords["language"] == "ja"
    assert keywords["tags"][0]["id"] == "logic"
    assert keywords["tags"][0]["displayNameJa"] == "Logic"
    assert keywords["tags"][0]["aliasesJa"] == ["Logic"]

    candidates = client.get(
        "/questions/candidates",
        params={"category": "Theory", "topic": "Logic"},
    ).json()
    assert candidates[0] | {
        "primaryTag": candidates[0]["primaryTag"],
        "topicTags": candidates[0]["topicTags"],
        "knowledgePoints": candidates[0]["knowledgePoints"],
        "syllabusArea": candidates[0]["syllabusArea"],
    } == {
        "questionId": 1,
        "sourcePageLabel": "R6",
        "sourcePageUrl": "https://example.test/r6",
        "examPart": "科目A",
        "questionNo": "Q1",
        "topic": "Logic",
        "category": "Theory",
        "questionUrl": "https://example.test/q1",
        "scrapedAt": "2026-01-01",
        "primaryTag": "logic",
        "topicTags": ["logic"],
        "knowledgePoints": ["logic"],
        "syllabusArea": "mathematics",
    }


def test_runtime_detail_endpoints_hide_answer_by_default(tmp_path: Path) -> None:
    db_path = _create_runtime_db(tmp_path)
    client = TestClient(create_app(settings=_settings(db_path, _create_keyword_files(tmp_path))))

    by_url = client.get(
        "/questions/by-url",
        params={"url": "https://example.test/q1"},
    ).json()
    by_id = client.get("/questions/1").json()

    assert by_url == by_id
    assert by_url["questionId"] == 1
    assert by_url["questionText"] == "2^5 question"
    assert by_url["choices"] == [
        {"label": "A", "text": "32"},
        {"label": "B", "text": "25"},
    ]
    assert "answer" not in by_url
    assert "explanation" not in by_url


def test_runtime_detail_endpoints_include_answer_when_requested(tmp_path: Path) -> None:
    db_path = _create_runtime_db(tmp_path)
    client = TestClient(create_app(settings=_settings(db_path, _create_keyword_files(tmp_path))))

    response = client.get(
        "/questions/by-url",
        params={"url": "https://example.test/q1", "includeAnswer": "true"},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "A"
    assert response.json()["explanation"] == "Power explanation"


def test_runtime_detail_normalizes_image_metadata(tmp_path: Path) -> None:
    db_path = _create_runtime_db(tmp_path)
    client = TestClient(create_app(settings=_settings(db_path, _create_keyword_files(tmp_path))))

    response = client.get("/questions/1")

    assert response.status_code == 200
    body = response.json()
    assert body["hasImages"] is True
    assert body["images"] == [
        {
            "publicPath": "/assets/fe-siken/r07_haru/q28.png",
            "alt": "diagram",
        },
        {
            "publicPath": "/assets/fe-siken/q29.png",
        },
    ]


def test_runtime_batch_details_preserve_request_order_and_include_topic_metadata(
    tmp_path: Path,
) -> None:
    db_path = _create_runtime_db(tmp_path)
    client = TestClient(create_app(settings=_settings(db_path, _create_keyword_files(tmp_path))))

    response = client.post(
        "/questions/details/batch",
        json={
            "urls": ["https://example.test/q2", "https://example.test/q1"],
            "includeAnswer": False,
            "includeExplanation": False,
        },
    )

    assert response.status_code == 200
    assert [item["questionUrl"] for item in response.json()["items"]] == [
        "https://example.test/q2",
        "https://example.test/q1",
    ]
    assert all("answer" not in item for item in response.json()["items"])
    assert response.json()["items"][0]["primaryTag"] == "sql_select"
    assert response.json()["items"][0]["topicTags"] == ["sql"]
    assert response.json()["items"][0]["knowledgePoints"] == ["sql_select"]
    assert response.json()["items"][0]["syllabusArea"] == "database"


def test_runtime_search_candidates_accepts_keywords_and_returns_shortage(
    tmp_path: Path,
) -> None:
    db_path = _create_runtime_db(tmp_path)
    client = TestClient(create_app(settings=_settings(db_path, _create_keyword_files(tmp_path))))

    logic_response = client.post(
        "/questions/candidates/search",
        json={"keywords": ["logic"], "topicTags": ["logic"], "limit": 10},
    )
    sql_response = client.post(
        "/questions/candidates/search",
        json={"keywords": ["SQL"], "topicTags": ["sql"], "limit": 10},
    )
    unknown_response = client.post(
        "/questions/candidates/search",
        json={"keywords": ["__NO_SUCH_FE_TOPIC__"], "limit": 5},
    )

    assert logic_response.status_code == 200
    assert sql_response.status_code == 200
    assert unknown_response.status_code == 200
    assert [item["questionId"] for item in logic_response.json()["questions"]] == [1]
    assert [item["questionId"] for item in sql_response.json()["questions"]] == [2]
    assert logic_response.json()["questions"] != sql_response.json()["questions"]
    assert logic_response.json()["questions"][0]["topicTags"] == ["logic"]
    assert sql_response.json()["questions"][0]["topicTags"] == ["sql"]
    assert unknown_response.json()["questions"] == []
    assert unknown_response.json()["totalMatched"] == 0
    assert unknown_response.json()["shortage"]["reason"] == "no_topic_matches"


def test_runtime_returns_404_for_missing_detail(tmp_path: Path) -> None:
    db_path = _create_runtime_db(tmp_path)
    client = TestClient(create_app(settings=_settings(db_path, _create_keyword_files(tmp_path))))

    response = client.get("/questions/999")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "question_not_found"


def _settings(db_path: Path, keyword_paths: tuple[Path, Path]) -> Settings:
    return Settings(
        database_path=db_path,
        asset_root=Path("public/assets/fe-siken"),
        read_only=True,
        enable_admin_api=False,
        admin_api_token=None,
        keyword_taxonomy_path=keyword_paths[0],
        question_topic_mappings_path=keyword_paths[1],
    )


def _create_keyword_files(tmp_path: Path) -> tuple[Path, Path]:
    taxonomy_path = tmp_path / "question_keyword_taxonomy.json"
    mappings_path = tmp_path / "question_topic_mappings.json"
    taxonomy_path.write_text(
        json.dumps(
            {
                "version": 1,
                "language": "ja",
                "tags": [
                    {
                        "id": "logic",
                        "level": "topicTag",
                        "displayNameJa": "Logic",
                        "aliasesJa": ["Logic"],
                        "aliasesEn": ["logic"],
                        "parentId": "mathematics",
                        "syllabusArea": "mathematics",
                    },
                    {
                        "id": "sql",
                        "level": "topicTag",
                        "displayNameJa": "SQL",
                        "aliasesJa": ["SQL"],
                        "aliasesEn": ["sql"],
                        "parentId": "database",
                        "syllabusArea": "database",
                    },
                    {
                        "id": "sql_select",
                        "level": "knowledgePoint",
                        "displayNameJa": "SQL SELECT",
                        "aliasesJa": ["SQL SELECT"],
                        "aliasesEn": ["select"],
                        "parentId": "sql",
                        "syllabusArea": "database",
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    mappings_path.write_text(
        json.dumps(
            {
                "version": 1,
                "language": "ja",
                "mappings": [
                    {
                        "questionUrl": "https://example.test/q1",
                        "examPart": "科目A",
                        "primaryTag": "logic",
                        "topicTags": ["logic"],
                        "knowledgePoints": ["logic"],
                        "syllabusArea": "mathematics",
                        "matchedEvidence": [],
                        "confidence": 0.94,
                        "needsHumanReview": False,
                    },
                    {
                        "questionUrl": "https://example.test/q2",
                        "examPart": "科目A",
                        "primaryTag": "sql_select",
                        "topicTags": ["sql"],
                        "knowledgePoints": ["sql_select"],
                        "syllabusArea": "database",
                        "matchedEvidence": [],
                        "confidence": 0.94,
                        "needsHumanReview": False,
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return taxonomy_path, mappings_path


def _create_runtime_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "questions.sqlite"
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE questions (
            id INTEGER PRIMARY KEY,
            source_page_label TEXT NOT NULL,
            source_page_url TEXT NOT NULL,
            exam_part TEXT NOT NULL,
            question_no TEXT NOT NULL,
            topic TEXT NOT NULL,
            category TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            scraped_at TEXT NOT NULL
        );
        CREATE TABLE question_details (
            question_url TEXT PRIMARY KEY,
            question_text TEXT NOT NULL,
            choices_json TEXT NOT NULL,
            answer TEXT NOT NULL,
            explanation TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            images_json TEXT NOT NULL DEFAULT '[]',
            has_images INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    conn.executemany(
        """
        INSERT INTO questions (
            id, source_page_label, source_page_url, exam_part, question_no, topic,
            category, url, scraped_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                1,
                "R6",
                "https://example.test/r6",
                "科目A",
                "Q1",
                "Logic",
                "Theory",
                "https://example.test/q1",
                "2026-01-01",
            ),
            (
                2,
                "R6",
                "https://example.test/r6",
                "科目A",
                "Q2",
                "SQL",
                "Database",
                "https://example.test/q2",
                "2026-01-01",
            ),
        ],
    )
    conn.executemany(
        """
        INSERT INTO question_details (
            question_url, question_text, choices_json, answer, explanation, fetched_at,
            images_json, has_images
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                "https://example.test/q1",
                "2^5 question",
                json.dumps(
                    [{"label": "A", "text": "32"}, {"label": "B", "text": "25"}],
                    ensure_ascii=False,
                ),
                "A",
                "Power explanation",
                "2026-01-02",
                json.dumps(
                    [
                        {
                            "public_path": "assets/fe-siken/r07_haru/q28.png",
                            "local_path": "/app/public/assets/fe-siken/r07_haru/q28.png",
                            "alt": "diagram",
                        },
                        {
                            "localPath": "C:/cache/q29.png",
                        },
                    ],
                    ensure_ascii=False,
                ),
                1,
            ),
            (
                "https://example.test/q2",
                "SQL question",
                json.dumps([{"label": "A", "text": "SELECT"}], ensure_ascii=False),
                "A",
                "SQL explanation",
                "2026-01-02",
                "[]",
                0,
            ),
        ],
    )
    conn.commit()
    conn.close()
    return db_path
