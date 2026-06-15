from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class QuestionTopicMetadata:
    primary_tag: str
    topic_tags: list[str]
    knowledge_points: list[str]
    syllabus_area: str


@dataclass(frozen=True)
class KeywordMatchResult:
    question_urls: list[str]
    total_matched: int


class KeywordIndex:
    def __init__(
        self,
        taxonomy: dict[str, Any],
        mappings: list[dict[str, Any]],
    ) -> None:
        self.taxonomy = taxonomy
        self._mappings = mappings
        self._mapping_by_url = {
            mapping["questionUrl"]: mapping
            for mapping in mappings
            if isinstance(mapping.get("questionUrl"), str)
        }
        self._tag_by_search_term = self._build_search_terms(taxonomy.get("tags", []))

    @classmethod
    def from_files(cls, taxonomy_path: Path, mappings_path: Path) -> KeywordIndex:
        taxonomy = _read_json_object(
            taxonomy_path,
            default={"version": 1, "language": "ja", "tags": []},
        )
        mappings = _read_json_object(
            mappings_path,
            default={"version": 1, "language": "ja", "mappings": []},
        ).get("mappings", [])
        if not isinstance(mappings, list):
            mappings = []
        return cls(taxonomy, mappings)

    def metadata_for_url(self, question_url: str) -> QuestionTopicMetadata | None:
        mapping = self._mapping_by_url.get(question_url)
        if mapping is None:
            return None
        return QuestionTopicMetadata(
            primary_tag=str(mapping.get("primaryTag", "")),
            topic_tags=_string_list(mapping.get("topicTags")),
            knowledge_points=_string_list(mapping.get("knowledgePoints")),
            syllabus_area=str(mapping.get("syllabusArea", "")),
        )

    def find_urls(
        self,
        *,
        exam_part: str | None,
        keywords: list[str],
        topic_tags: list[str],
        knowledge_points: list[str],
        syllabus_area: str | None,
        limit: int,
        offset: int,
    ) -> KeywordMatchResult:
        resolved_keyword_tags = {
            self._tag_id_for_keyword(keyword)
            for keyword in keywords
            if self._tag_id_for_keyword(keyword)
        }
        if keywords and not resolved_keyword_tags:
            return KeywordMatchResult(question_urls=[], total_matched=0)

        requested_tags = set(topic_tags)
        requested_knowledge_points = set(knowledge_points)
        requested_tags.update(resolved_keyword_tags)
        requested_tags.discard("")

        matched_urls: list[str] = []
        for mapping in self._mappings:
            if exam_part and mapping.get("examPart") != exam_part:
                continue
            if syllabus_area and mapping.get("syllabusArea") != syllabus_area:
                continue
            mapping_topic_tags = set(_string_list(mapping.get("topicTags")))
            mapping_knowledge_points = set(_string_list(mapping.get("knowledgePoints")))
            if requested_tags and not requested_tags.intersection(
                {str(mapping.get("primaryTag", "")), *mapping_topic_tags, *mapping_knowledge_points}
            ):
                continue
            if requested_knowledge_points and not requested_knowledge_points.intersection(
                mapping_knowledge_points
            ):
                continue
            question_url = mapping.get("questionUrl")
            if isinstance(question_url, str):
                matched_urls.append(question_url)

        return KeywordMatchResult(
            question_urls=matched_urls[offset : offset + limit],
            total_matched=len(matched_urls),
        )

    def _tag_id_for_keyword(self, keyword: str) -> str:
        return self._tag_by_search_term.get(keyword.strip().lower(), "")

    @staticmethod
    def _build_search_terms(tags: Any) -> dict[str, str]:
        if not isinstance(tags, list):
            return {}
        terms: dict[str, str] = {}
        for tag in tags:
            if not isinstance(tag, dict) or not isinstance(tag.get("id"), str):
                continue
            tag_id = tag["id"]
            values = [tag_id, tag.get("displayNameJa"), tag.get("displayNameEn")]
            values.extend(_string_list(tag.get("aliasesJa")))
            values.extend(_string_list(tag.get("aliasesEn")))
            for value in values:
                if isinstance(value, str) and value.strip():
                    terms[value.strip().lower()] = tag_id
        return terms


def _read_json_object(path: Path, *, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    parsed = json.loads(path.read_text(encoding="utf-8"))
    return parsed if isinstance(parsed, dict) else default


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]
