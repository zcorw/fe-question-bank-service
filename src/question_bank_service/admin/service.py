import json
import sqlite3
from collections.abc import Callable
from datetime import UTC, datetime

from question_bank_service.config import Settings
from question_bank_service.db.repositories import QuestionBankRepository
from question_bank_service.db.sqlite import open_sqlite_connection
from question_bank_service.scraper.html_parser import (
    ParsedQuestionDetail,
    parse_question_detail_html,
)


class AdminService:
    def __init__(self, *, settings: Settings, detail_html_fetcher: Callable[[str], str]) -> None:
        self._settings = settings
        self._detail_html_fetcher = detail_html_fetcher

    def refresh_question(self, url: str, *, force: bool) -> bool:
        html = self._detail_html_fetcher(url)
        detail = parse_question_detail_html(html, question_url=url)

        with open_sqlite_connection(self._settings.database_path, read_only=False) as connection:
            if not force and self._detail_exists(connection, url):
                return False
            self._upsert_detail(connection, detail)
            connection.commit()
        return True

    def validate_cache(self, urls: list[str]) -> list[dict[str, str]]:
        failures: list[dict[str, str]] = []
        with open_sqlite_connection(
            self._settings.database_path,
            read_only=self._settings.read_only,
        ) as connection:
            repository = QuestionBankRepository(connection)
            for url in urls:
                if repository.get_detail_by_url(url) is None:
                    failures.append(
                        {
                            "url": url,
                            "code": "detail_missing",
                            "message": "Question detail is missing",
                        }
                    )
        return failures

    def _detail_exists(self, connection: sqlite3.Connection, url: str) -> bool:
        row = connection.execute(
            "SELECT 1 FROM question_details WHERE question_url = ?",
            [url],
        ).fetchone()
        return row is not None

    def _upsert_detail(self, connection: sqlite3.Connection, detail: ParsedQuestionDetail) -> None:
        fetched_at = datetime.now(UTC).isoformat()
        connection.execute(
            """
            INSERT INTO question_details (
                question_url, question_text, choices_json, answer, explanation, fetched_at,
                images_json, has_images
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(question_url) DO UPDATE SET
                question_text = excluded.question_text,
                choices_json = excluded.choices_json,
                answer = excluded.answer,
                explanation = excluded.explanation,
                fetched_at = excluded.fetched_at,
                images_json = excluded.images_json,
                has_images = excluded.has_images
            """,
            [
                detail.question_url,
                detail.question_text,
                json.dumps(detail.choices, ensure_ascii=False),
                detail.answer,
                detail.explanation,
                fetched_at,
                json.dumps(detail.images, ensure_ascii=False),
                int(detail.has_images),
            ],
        )
