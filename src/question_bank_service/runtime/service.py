from collections.abc import Callable
from types import TracebackType

from question_bank_service.db.repositories import (
    Keywords,
    QuestionBankRepository,
    QuestionCandidate,
    QuestionDetail,
)


class RuntimeService:
    def __init__(self, repository: QuestionBankRepository, *, close: Callable[[], None]) -> None:
        self._repository = repository
        self._close = close

    def __enter__(self) -> "RuntimeService":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._close()

    def list_keywords(self) -> Keywords:
        return self._repository.list_keywords()

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
        return self._repository.find_candidates(
            category=category,
            categories=categories,
            topic=topic,
            url=url,
            limit=limit,
            offset=offset,
        )

    def get_detail_by_url(self, question_url: str) -> QuestionDetail | None:
        return self._repository.get_detail_by_url(question_url)

    def get_detail_by_id(self, question_id: int) -> QuestionDetail | None:
        return self._repository.get_detail_by_id(question_id)

    def get_details_by_urls(self, question_urls: list[str]) -> list[QuestionDetail]:
        return self._repository.get_details_by_urls(question_urls)

    def candidate_to_response(self, candidate: QuestionCandidate) -> dict[str, object]:
        return {
            "questionId": candidate.question_id,
            "sourcePageLabel": candidate.source_page_label,
            "sourcePageUrl": candidate.source_page_url,
            "examPart": candidate.exam_part,
            "questionNo": candidate.question_no,
            "topic": candidate.topic,
            "category": candidate.category,
            "questionUrl": candidate.question_url,
            "scrapedAt": candidate.scraped_at,
        }

    def detail_to_response(
        self,
        detail: QuestionDetail,
        *,
        include_answer: bool,
        include_explanation: bool,
    ) -> dict[str, object]:
        response: dict[str, object] = {
            "questionId": detail.question_id,
            "questionUrl": detail.question_url,
            "sourceUrl": detail.source_url,
            "questionText": detail.question_text,
            "choices": [
                {"label": choice.label, "text": choice.text}
                for choice in detail.choices
            ],
            "hasImages": detail.has_images,
            "images": detail.images,
            "fetchedAt": detail.fetched_at,
        }
        if include_answer:
            response["answer"] = detail.answer
        if include_explanation:
            response["explanation"] = detail.explanation
        return response
