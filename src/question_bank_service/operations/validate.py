import argparse
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from question_bank_service.db.repositories import QuestionBankRepository, RepositoryError
from question_bank_service.db.sqlite import open_sqlite_connection


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    failures: list[dict[str, str]]


def validate_question_bank(database_path: Path) -> ValidationResult:
    failures: list[dict[str, str]] = []
    with open_sqlite_connection(database_path, read_only=True) as connection:
        repository = QuestionBankRepository(connection)
        for row in _runtime_questions(connection):
            url = row["url"]
            try:
                detail = repository.get_detail_by_url(url)
            except RepositoryError as exc:
                failures.append(
                    {
                        "code": "detail_invalid",
                        "message": str(exc),
                        "url": url,
                    }
                )
                continue

            if detail is None:
                failures.append(
                    {
                        "code": "detail_missing",
                        "message": "Question is missing detail cache",
                        "url": url,
                    }
                )
    return ValidationResult(ok=not failures, failures=failures)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate question bank release readiness.")
    parser.add_argument("--db-path", type=Path, default=Path("data/fe_siken_questions.sqlite"))
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    result = validate_question_bank(args.db_path)
    if args.json:
        print(json.dumps({"ok": result.ok, "failures": result.failures}, ensure_ascii=False))
    else:
        if result.ok:
            print("question bank validation passed")
        else:
            for failure in result.failures:
                print(f"{failure['code']}: {failure['url']} - {failure['message']}")

    raise SystemExit(0 if result.ok else 1)


def _runtime_questions(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT url
        FROM questions
        WHERE exam_part = ?
        ORDER BY id
        """,
        ["科目A"],
    ).fetchall()


if __name__ == "__main__":
    main()
