import argparse
import json
from pathlib import Path
from typing import Protocol
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from question_bank_service.db.repositories import QuestionBankRepository
from question_bank_service.db.sqlite import open_sqlite_connection


class RuntimeQuestionBankClient(Protocol):
    def find_candidates(self, *, category: str | None, limit: int) -> list[dict[str, object]]:
        ...

    def get_details_by_urls(
        self,
        urls: list[str],
        *,
        include_answer: bool,
        include_explanation: bool,
    ) -> list[dict[str, object]]:
        ...


def generate_daily_practice_markdown(
    client: RuntimeQuestionBankClient,
    *,
    title: str,
    category: str | None,
    limit: int,
) -> str:
    candidates = client.find_candidates(category=category, limit=limit)
    urls = [_required_string(candidate, "questionUrl") for candidate in candidates]
    details = client.get_details_by_urls(
        urls,
        include_answer=False,
        include_explanation=False,
    )
    question_numbers = {
        _required_string(candidate, "questionUrl"): str(candidate.get("questionNo") or "")
        for candidate in candidates
    }

    lines = [f"# {title}", ""]
    for index, detail in enumerate(details, start=1):
        question_url = _required_string(detail, "questionUrl")
        question_no = question_numbers.get(question_url) or f"Q{index}"
        lines.extend(
            [
                f"## {index}. {question_no}",
                "",
                _required_string(detail, "questionText"),
                "",
            ]
        )
        for choice in detail.get("choices", []):
            if not isinstance(choice, dict):
                continue
            label = choice.get("label")
            text = choice.get("text")
            if isinstance(label, str) and isinstance(text, str):
                lines.append(f"- {label}. {text}")
        lines.extend(["", f"出典: {question_url}", ""])

    return "\n".join(lines).rstrip() + "\n"


class HttpRuntimeQuestionBankClient:
    def __init__(self, *, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    def find_candidates(self, *, category: str | None, limit: int) -> list[dict[str, object]]:
        params: dict[str, str | int] = {"limit": limit}
        if category:
            params["category"] = category
        return _get_json(f"{self._base_url}/questions/candidates?{urlencode(params)}")

    def get_details_by_urls(
        self,
        urls: list[str],
        *,
        include_answer: bool,
        include_explanation: bool,
    ) -> list[dict[str, object]]:
        response = _post_json(
            f"{self._base_url}/questions/details/batch",
            {
                "urls": urls,
                "includeAnswer": include_answer,
                "includeExplanation": include_explanation,
            },
        )
        items = response.get("items") if isinstance(response, dict) else None
        if not isinstance(items, list):
            raise ValueError("Runtime API batch response did not include items")
        return items


class LocalRuntimeQuestionBankClient:
    def __init__(self, *, database_path: Path) -> None:
        self._database_path = database_path

    def find_candidates(self, *, category: str | None, limit: int) -> list[dict[str, object]]:
        with open_sqlite_connection(self._database_path, read_only=True) as connection:
            repository = QuestionBankRepository(connection)
            candidates = repository.find_candidates(category=category, limit=limit)
        return [
            {
                "questionNo": candidate.question_no,
                "questionUrl": candidate.question_url,
            }
            for candidate in candidates
        ]

    def get_details_by_urls(
        self,
        urls: list[str],
        *,
        include_answer: bool,
        include_explanation: bool,
    ) -> list[dict[str, object]]:
        with open_sqlite_connection(self._database_path, read_only=True) as connection:
            repository = QuestionBankRepository(connection)
            details = repository.get_details_by_urls(urls)
        rows: list[dict[str, object]] = []
        for detail in details:
            row: dict[str, object] = {
                "questionUrl": detail.question_url,
                "questionText": detail.question_text,
                "choices": [
                    {"label": choice.label, "text": choice.text}
                    for choice in detail.choices
                ],
            }
            if include_answer:
                row["answer"] = detail.answer
            if include_explanation:
                row["explanation"] = detail.explanation
            rows.append(row)
        return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a daily FE practice document.")
    parser.add_argument("--base-url", help="Runtime API base URL, for example http://127.0.0.1:8000")
    parser.add_argument("--db-path", type=Path, default=Path("data/fe_siken_questions.sqlite"))
    parser.add_argument("--category")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--title", default="今日の練習")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    client: RuntimeQuestionBankClient
    if args.base_url:
        client = HttpRuntimeQuestionBankClient(base_url=args.base_url)
    else:
        client = LocalRuntimeQuestionBankClient(database_path=args.db_path)

    markdown = generate_daily_practice_markdown(
        client,
        title=args.title,
        category=args.category,
        limit=args.limit,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")


def _get_json(url: str) -> object:
    with urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _post_json(url: str, payload: dict[str, object]) -> object:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _required_string(row: dict[str, object], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str):
        raise ValueError(f"Expected string field: {key}")
    return value


if __name__ == "__main__":
    main()
