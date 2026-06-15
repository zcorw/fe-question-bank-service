from pydantic import BaseModel, Field


class CandidateSearchRequest(BaseModel):
    exam_part: str = Field(default="科目A", alias="examPart")
    keywords: list[str] | None = None
    topic_tags: list[str] | None = Field(default=None, alias="topicTags")
    knowledge_points: list[str] | None = Field(default=None, alias="knowledgePoints")
    syllabus_area: str | None = Field(default=None, alias="syllabusArea")
    categories: list[str] | None = None
    topic: str | None = None
    url: str | None = None
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class BatchDetailRequest(BaseModel):
    urls: list[str] = Field(min_length=1)
    include_answer: bool = Field(default=False, alias="includeAnswer")
    include_explanation: bool = Field(default=False, alias="includeExplanation")
