import json
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from question_bank_service.app import create_app
from question_bank_service.config import Settings


def test_runtime_api_exposes_read_only_question_bank(tmp_path: Path) -> None:
    db_path = _create_runtime_db(tmp_path)
    client = TestClient(create_app(settings=_settings(db_path)))

    assert client.get("/health").json() == {
        "ok": True,
        "database": "ready",
        "readOnly": True,
    }

    assert client.get("/keywords").json() == {
        "categories": ["データベース", "基礎理論"],
        "topics": ["SQL", "論理演算"],
    }

    candidates = client.get(
        "/questions/candidates",
        params={"category": "基礎理論", "topic": "論理演算"},
    ).json()
    assert candidates == [
        {
            "questionId": 1,
            "sourcePageLabel": "令和6年秋",
            "sourcePageUrl": "https://example.test/r6",
            "examPart": "科目A",
            "questionNo": "問1",
            "topic": "論理演算",
            "category": "基礎理論",
            "questionUrl": "https://example.test/q1",
            "scrapedAt": "2026-01-01",
        }
    ]


def test_runtime_detail_endpoints_hide_answer_by_default(tmp_path: Path) -> None:
    db_path = _create_runtime_db(tmp_path)
    client = TestClient(create_app(settings=_settings(db_path)))

    by_url = client.get(
        "/questions/by-url",
        params={"url": "https://example.test/q1"},
    ).json()
    by_id = client.get("/questions/1").json()

    assert by_url == by_id
    assert by_url["questionId"] == 1
    assert by_url["questionText"] == "2^5 と ¬x を含む問題"
    assert by_url["choices"] == [
        {"label": "ア", "text": "32"},
        {"label": "イ", "text": "25"},
    ]
    assert "answer" not in by_url
    assert "explanation" not in by_url


def test_runtime_detail_endpoints_include_answer_when_requested(tmp_path: Path) -> None:
    db_path = _create_runtime_db(tmp_path)
    client = TestClient(create_app(settings=_settings(db_path)))

    response = client.get(
        "/questions/by-url",
        params={"url": "https://example.test/q1", "includeAnswer": "true"},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "ア"
    assert response.json()["explanation"] == "指数を保つ"


def test_runtime_detail_normalizes_image_metadata(tmp_path: Path) -> None:
    db_path = _create_runtime_db(tmp_path)
    client = TestClient(create_app(settings=_settings(db_path)))

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


def test_runtime_batch_details_preserve_request_order(tmp_path: Path) -> None:
    db_path = _create_runtime_db(tmp_path)
    client = TestClient(create_app(settings=_settings(db_path)))

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


def test_runtime_search_candidates_accepts_multiple_categories(tmp_path: Path) -> None:
    db_path = _create_runtime_db(tmp_path)
    client = TestClient(create_app(settings=_settings(db_path)))

    response = client.post(
        "/questions/candidates/search",
        json={"categories": ["基礎理論", "データベース"], "limit": 10},
    )

    assert response.status_code == 200
    assert [item["questionId"] for item in response.json()] == [1, 2]


def test_runtime_returns_404_for_missing_detail(tmp_path: Path) -> None:
    db_path = _create_runtime_db(tmp_path)
    client = TestClient(create_app(settings=_settings(db_path)))

    response = client.get("/questions/999")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "question_not_found"


def _settings(db_path: Path) -> Settings:
    return Settings(
        database_path=db_path,
        asset_root=Path("public/assets/fe-siken"),
        read_only=True,
        enable_admin_api=False,
        admin_api_token=None,
    )


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
                "令和6年秋",
                "https://example.test/r6",
                "科目A",
                "問1",
                "論理演算",
                "基礎理論",
                "https://example.test/q1",
                "2026-01-01",
            ),
            (
                2,
                "令和6年秋",
                "https://example.test/r6",
                "科目A",
                "問2",
                "SQL",
                "データベース",
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
                "2^5 と ¬x を含む問題",
                json.dumps(
                    [{"label": "ア", "text": "32"}, {"label": "イ", "text": "25"}],
                    ensure_ascii=False,
                ),
                "ア",
                "指数を保つ",
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
                "SQL の問題",
                json.dumps([{"label": "ア", "text": "SELECT"}], ensure_ascii=False),
                "ア",
                "説明",
                "2026-01-02",
                "[]",
                0,
            ),
        ],
    )
    conn.commit()
    conn.close()
    return db_path
