from pydantic import BaseModel, Field


class RefreshQuestionRequest(BaseModel):
    url: str
    force: bool = False


class ValidateCacheRequest(BaseModel):
    urls: list[str] = Field(min_length=1)
    checks: list[str] = Field(default_factory=list)
