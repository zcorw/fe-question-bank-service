from fastapi import APIRouter, HTTPException, Query

from question_bank_service.config import Settings
from question_bank_service.db.repositories import QuestionBankRepository
from question_bank_service.db.sqlite import open_sqlite_connection
from question_bank_service.runtime.schemas import BatchDetailRequest, CandidateSearchRequest
from question_bank_service.runtime.service import RuntimeService


def create_runtime_router(settings: Settings) -> APIRouter:
    router = APIRouter()

    def service() -> RuntimeService:
        connection = open_sqlite_connection(settings.database_path, read_only=settings.read_only)
        return RuntimeService(QuestionBankRepository(connection), close=connection.close)

    @router.get("/keywords")
    def keywords() -> dict[str, list[str]]:
        with service() as runtime:
            result = runtime.list_keywords()
        return {"categories": result.categories, "topics": result.topics}

    @router.get("/questions/candidates")
    def candidates(
        category: str | None = None,
        topic: str | None = None,
        url: str | None = None,
        limit: int = Query(default=100, ge=1, le=500),
        offset: int = Query(default=0, ge=0),
    ) -> list[dict[str, object]]:
        with service() as runtime:
            return [
                runtime.candidate_to_response(candidate)
                for candidate in runtime.find_candidates(
                    category=category,
                    topic=topic,
                    url=url,
                    limit=limit,
                    offset=offset,
                )
            ]

    @router.post("/questions/candidates/search")
    def search_candidates(request: CandidateSearchRequest) -> list[dict[str, object]]:
        with service() as runtime:
            return [
                runtime.candidate_to_response(candidate)
                for candidate in runtime.find_candidates(
                    categories=request.categories,
                    topic=request.topic,
                    url=request.url,
                    limit=request.limit,
                    offset=request.offset,
                )
            ]

    @router.get("/questions/by-url")
    def detail_by_url(
        url: str,
        include_answer: bool = Query(default=False, alias="includeAnswer"),
        include_explanation: bool | None = Query(default=None, alias="includeExplanation"),
    ) -> dict[str, object]:
        with service() as runtime:
            detail = runtime.get_detail_by_url(url)
            if detail is None:
                raise _not_found()
            return runtime.detail_to_response(
                detail,
                include_answer=include_answer,
                include_explanation=_include_explanation(include_answer, include_explanation),
            )

    @router.get("/questions/{question_id}")
    def detail_by_id(
        question_id: int,
        include_answer: bool = Query(default=False, alias="includeAnswer"),
        include_explanation: bool | None = Query(default=None, alias="includeExplanation"),
    ) -> dict[str, object]:
        with service() as runtime:
            detail = runtime.get_detail_by_id(question_id)
            if detail is None:
                raise _not_found()
            return runtime.detail_to_response(
                detail,
                include_answer=include_answer,
                include_explanation=_include_explanation(include_answer, include_explanation),
            )

    @router.post("/questions/details/batch")
    def batch_details(request: BatchDetailRequest) -> dict[str, list[dict[str, object]]]:
        with service() as runtime:
            details = runtime.get_details_by_urls(request.urls)
            return {
                "items": [
                    runtime.detail_to_response(
                        detail,
                        include_answer=request.include_answer,
                        include_explanation=request.include_explanation,
                    )
                    for detail in details
                ]
            }

    return router


def _include_explanation(include_answer: bool, include_explanation: bool | None) -> bool:
    return include_answer if include_explanation is None else include_explanation


def _not_found() -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={
            "code": "question_not_found",
            "message": "Question detail was not found",
        },
    )
