import sqlite3
from pathlib import Path

from question_bank_service.operations.backup import backup_database
from question_bank_service.operations.validate import validate_question_bank


def test_backup_database_creates_timestamped_copy(tmp_path: Path) -> None:
    db_path = tmp_path / "fe_siken_questions.sqlite"
    db_path.write_bytes(b"sqlite-content")
    backup_dir = tmp_path / "backups"

    backup_path = backup_database(db_path, backup_dir=backup_dir, timestamp="20260609123045")

    assert backup_path == backup_dir / "fe_siken_questions.sqlite.20260609123045.bak"
    assert backup_path.read_bytes() == b"sqlite-content"


def test_validate_question_bank_reports_missing_details(tmp_path: Path) -> None:
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
        INSERT INTO questions (
            id, source_page_label, source_page_url, exam_part, question_no, topic,
            category, url, scraped_at
        ) VALUES (
            1, '令和6年秋', 'https://example.test/r6', '科目A', '問1',
            '論理演算', '基礎理論', 'https://example.test/q1', '2026-01-01'
        );
        """
    )
    conn.close()

    result = validate_question_bank(db_path)

    assert result.ok is False
    assert result.failures == [
        {
            "code": "detail_missing",
            "message": "Question is missing detail cache",
            "url": "https://example.test/q1",
        }
    ]
