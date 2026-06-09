import json
import sqlite3
from pathlib import Path

import pytest

from question_bank_service.db.repositories import QuestionBankRepository, RepositoryError
from question_bank_service.db.sqlite import open_sqlite_connection


@pytest.fixture()
def question_db(tmp_path: Path) -> Path:
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
    questions = [
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
        (
            3,
            "令和5年春",
            "https://example.test/r5",
            "科目B",
            "問1",
            "除外",
            "除外",
            "https://example.test/q3",
            "2026-01-01",
        ),
    ]
    conn.executemany(
        """
        INSERT INTO questions (
            id, source_page_label, source_page_url, exam_part, question_no, topic,
            category, url, scraped_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        questions,
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
                    [
                        {"label": "ア", "text": "32"},
                        {"label": "イ", "text": "25"},
                    ],
                    ensure_ascii=False,
                ),
                "ア",
                "指数を保つ",
                "2026-01-02",
                json.dumps([{"publicPath": "/assets/q1.png"}]),
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


def test_open_sqlite_connection_uses_read_only_mode(question_db: Path) -> None:
    conn = open_sqlite_connection(question_db, read_only=True)

    with pytest.raises(sqlite3.OperationalError):
        conn.execute("CREATE TABLE should_fail (id INTEGER)")

    conn.close()


def test_repository_lists_keywords_for_runtime_exam_part(question_db: Path) -> None:
    with open_sqlite_connection(question_db, read_only=True) as conn:
        keywords = QuestionBankRepository(conn).list_keywords()

    assert keywords.categories == ["データベース", "基礎理論"]
    assert keywords.topics == ["SQL", "論理演算"]


def test_repository_finds_candidates_with_filters(question_db: Path) -> None:
    with open_sqlite_connection(question_db, read_only=True) as conn:
        candidates = QuestionBankRepository(conn).find_candidates(
            category="基礎理論",
            topic="論理演算",
            limit=10,
        )

    assert [candidate.question_id for candidate in candidates] == [1]
    assert candidates[0].question_url == "https://example.test/q1"
    assert candidates[0].exam_part == "科目A"


def test_repository_gets_detail_by_url_and_id(question_db: Path) -> None:
    with open_sqlite_connection(question_db, read_only=True) as conn:
        repository = QuestionBankRepository(conn)
        by_url = repository.get_detail_by_url("https://example.test/q1")
        by_id = repository.get_detail_by_id(1)

    assert by_url == by_id
    assert by_url is not None
    assert by_url.question_id == 1
    assert by_url.source_url == "https://example.test/q1"
    assert by_url.choices[0].label == "ア"
    assert by_url.images == [{"publicPath": "/assets/q1.png"}]
    assert by_url.has_images is True


def test_repository_returns_batch_details_in_requested_url_order(question_db: Path) -> None:
    with open_sqlite_connection(question_db, read_only=True) as conn:
        details = QuestionBankRepository(conn).get_details_by_urls(
            ["https://example.test/q2", "https://example.test/q1"]
        )

    assert [detail.question_url for detail in details] == [
        "https://example.test/q2",
        "https://example.test/q1",
    ]


def test_repository_raises_for_invalid_json(question_db: Path) -> None:
    conn = sqlite3.connect(question_db)
    conn.execute(
        "UPDATE question_details SET choices_json = ? WHERE question_url = ?",
        ("not-json", "https://example.test/q1"),
    )
    conn.commit()
    conn.close()

    with open_sqlite_connection(question_db, read_only=True) as readonly_conn:
        with pytest.raises(RepositoryError, match="Invalid choices_json"):
            QuestionBankRepository(readonly_conn).get_detail_by_url("https://example.test/q1")
