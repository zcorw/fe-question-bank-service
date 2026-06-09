import json
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from question_bank_service.app import create_app
from question_bank_service.config import Settings


def test_admin_api_requires_bearer_token(tmp_path: Path) -> None:
    db_path = _create_admin_db(tmp_path)
    client = TestClient(create_app(settings=_settings(db_path), detail_html_fetcher=_fetcher({})))

    response = client.post("/admin/questions/refresh", json={"url": "https://example.test/q1"})

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "unauthorized"


def test_admin_refresh_parses_and_writes_question_detail(tmp_path: Path) -> None:
    db_path = _create_admin_db(tmp_path)
    client = TestClient(
        create_app(
            settings=_settings(db_path),
            detail_html_fetcher=_fetcher({"https://example.test/q1": _detail_html()}),
        )
    )

    response = client.post(
        "/admin/questions/refresh",
        json={"url": "https://example.test/q1", "force": True},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.json() == {"url": "https://example.test/q1", "refreshed": True}

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        """
        SELECT question_text, choices_json, answer, explanation, has_images
        FROM question_details
        WHERE question_url = ?
        """,
        ["https://example.test/q1"],
    ).fetchone()
    conn.close()

    assert row is not None
    assert "2^5" in row[0]
    assert json.loads(row[1]) == [{"label": "ア", "text": "2^5"}]
    assert row[2] == "ア"
    assert "¬y" in row[3]
    assert row[4] == 1


def test_admin_validate_cache_reports_missing_details(tmp_path: Path) -> None:
    db_path = _create_admin_db(tmp_path)
    client = TestClient(create_app(settings=_settings(db_path), detail_html_fetcher=_fetcher({})))

    response = client.post(
        "/admin/questions/validate-cache",
        json={"urls": ["https://example.test/q1"], "checks": ["detail_exists"]},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "ok": False,
        "failures": [
            {
                "url": "https://example.test/q1",
                "code": "detail_missing",
                "message": "Question detail is missing",
            }
        ],
    }


def _settings(db_path: Path) -> Settings:
    return Settings(
        database_path=db_path,
        asset_root=Path("public/assets/fe-siken"),
        read_only=False,
        enable_admin_api=True,
        admin_api_token="test-token",
    )


def _fetcher(pages: dict[str, str]):
    def fetch(url: str) -> str:
        return pages[url]

    return fetch


def _create_admin_db(tmp_path: Path) -> Path:
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
    conn.execute(
        """
        INSERT INTO questions (
            id, source_page_label, source_page_url, exam_part, question_no, topic,
            category, url, scraped_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
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
    )
    conn.commit()
    conn.close()
    return db_path


def _detail_html() -> str:
    return """
    <section id="question">
      <p>値 2<sup>5</sup></p>
      <img src="/images/q1.png" alt="図1" />
    </section>
    <ol class="choices">
      <li><span class="choice-label">ア</span><span>2<sup>5</sup></span></li>
    </ol>
    <section id="answer">ア</section>
    <section id="explanation"><span class="overline">y</span></section>
    """
