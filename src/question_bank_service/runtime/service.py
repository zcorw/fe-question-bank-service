from collections.abc import Callable
from types import TracebackType

from question_bank_service.db.repositories import (
    Keywords,
    QuestionBankRepository,
    QuestionCandidate,
    QuestionDetail,
)
from question_bank_service.runtime.keyword_index import KeywordIndex


class RuntimeService:
    def __init__(
        self,
        repository: QuestionBankRepository,
        *,
        keyword_index: KeywordIndex,
        close: Callable[[], None],
    ) -> None:
        self._repository = repository
        self._keyword_index = keyword_index
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

    def list_keyword_taxonomy(self) -> dict[str, object]:
        return self._keyword_index.taxonomy

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

    def find_keyword_candidates(
        self,
        *,
        exam_part: str | None,
        keywords: list[str],
        topic_tags: list[str],
        knowledge_points: list[str],
        syllabus_area: str | None,
        limit: int,
        offset: int,
    ) -> dict[str, object]:
        match = self._keyword_index.find_urls(
            exam_part=exam_part,
            keywords=keywords,
            topic_tags=topic_tags,
            knowledge_points=knowledge_points,
            syllabus_area=syllabus_area,
            limit=limit,
            offset=offset,
        )
        candidates = [
            candidate
            for question_url in match.question_urls
            for candidate in self.find_candidates(url=question_url, limit=1)
        ]
        questions = [self.candidate_to_response(candidate) for candidate in candidates]
        response: dict[str, object] = {
            "questions": questions,
            "totalMatched": match.total_matched,
        }
        if len(questions) < limit:
            response["shortage"] = {
                "requested": limit,
                "returned": len(questions),
                "reason": "no_topic_matches"
                if match.total_matched == 0
                else "not_enough_topic_matches",
            }
        return response

    def candidate_to_response(self, candidate: QuestionCandidate) -> dict[str, object]:
        response: dict[str, object] = {
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
        response.update(self._topic_metadata_response(candidate.question_url))
        return response

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
        if detail.learning_explanation:
            response["learningExplanation"] = detail.learning_explanation
        if detail.explanation_ja:
            response["explanationJa"] = detail.explanation_ja
        if detail.distractor_explanations_ja:
            response["distractorExplanationsJa"] = detail.distractor_explanations_ja
        if detail.knowledge_point_ja:
            response["knowledgePointJa"] = detail.knowledge_point_ja
        if detail.exam_point_ja:
            response["examPointJa"] = detail.exam_point_ja
        if detail.common_trap_ja:
            response["commonTrapJa"] = detail.common_trap_ja
        response.update(self._topic_metadata_response(detail.question_url))
        return response

    def _topic_metadata_response(self, question_url: str) -> dict[str, object]:
        metadata = self._keyword_index.metadata_for_url(question_url)
        if metadata is None:
            return {}
        return {
            "primaryTag": metadata.primary_tag,
            "topicTags": metadata.topic_tags,
            "knowledgePoints": metadata.knowledge_points,
            "syllabusArea": metadata.syllabus_area,
        }
