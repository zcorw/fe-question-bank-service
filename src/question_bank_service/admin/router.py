from collections.abc import Callable

from fastapi import APIRouter, Header, HTTPException

from question_bank_service.admin.schemas import RefreshQuestionRequest, ValidateCacheRequest
from question_bank_service.admin.service import AdminService
from question_bank_service.config import Settings

DetailHtmlFetcher = Callable[[str], str]


def create_admin_router(
    settings: Settings,
    *,
    detail_html_fetcher: DetailHtmlFetcher | None,
) -> APIRouter:
    router = APIRouter(prefix="/admin")
    fetcher = detail_html_fetcher or _missing_fetcher

    def admin_service() -> AdminService:
        return AdminService(settings=settings, detail_html_fetcher=fetcher)

    def require_token(authorization: str | None) -> None:
        expected = f"Bearer {settings.admin_api_token}"
        if authorization != expected:
            raise HTTPException(
                status_code=401,
                detail={"code": "unauthorized", "message": "Admin token is missing or invalid"},
            )

    @router.post("/questions/refresh")
    def refresh_question(
        request: RefreshQuestionRequest,
        authorization: str | None = Header(default=None, alias="Authorization"),
    ) -> dict[str, object]:
        require_token(authorization)
        refreshed = admin_service().refresh_question(request.url, force=request.force)
        return {"url": request.url, "refreshed": refreshed}

    @router.post("/questions/validate-cache")
    def validate_cache(
        request: ValidateCacheRequest,
        authorization: str | None = Header(default=None, alias="Authorization"),
    ) -> dict[str, object]:
        require_token(authorization)
        failures = admin_service().validate_cache(request.urls)
        return {"ok": not failures, "failures": failures}

    return router


def _missing_fetcher(url: str) -> str:
    raise RuntimeError(f"No detail HTML fetcher configured for {url}")
