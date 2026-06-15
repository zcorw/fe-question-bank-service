import json
import sqlite3
from pathlib import Path


def test_generated_keyword_json_files_are_valid_and_cover_questions() -> None:
    taxonomy = _read_json(Path("data/question_keyword_taxonomy.json"))
    mappings = _read_json(Path("data/question_topic_mappings.json"))
    fixtures = _read_json(Path("data/question_keyword_search_fixtures.json"))

    assert taxonomy["version"] == 1
    assert taxonomy["language"] == "ja"
    assert taxonomy["tags"]
    assert mappings["version"] == 1
    assert mappings["language"] == "ja"
    assert mappings["mappings"]
    assert fixtures["version"] == 1
    assert fixtures["fixtures"]

    conn = sqlite3.connect("data/fe_siken_questions.sqlite")
    question_count = conn.execute("SELECT count(*) FROM questions").fetchone()[0]
    conn.close()

    question_urls = [mapping["questionUrl"] for mapping in mappings["mappings"]]
    assert len(question_urls) == question_count
    assert len(question_urls) == len(set(question_urls))


def test_high_frequency_fixtures_use_readable_canonical_tag_ids() -> None:
    taxonomy = _read_json(Path("data/question_keyword_taxonomy.json"))
    mappings = _read_json(Path("data/question_topic_mappings.json"))
    fixtures = _read_json(Path("data/question_keyword_search_fixtures.json"))

    tags_by_id = {tag["id"]: tag for tag in taxonomy["tags"]}
    for tag_id in [
        "transaction",
        "sql",
        "security",
        "network",
        "algorithm",
        "availability",
    ]:
        assert tag_id in tags_by_id
        assert tags_by_id[tag_id]["level"] == "topicTag"
        assert not tag_id.startswith("topic_")

    fixture_tag_ids = {
        tag_id
        for fixture in fixtures["fixtures"]
        for tag_id in fixture.get("query", {}).get("topicTags", [])
    }
    assert {"transaction", "sql", "security", "network", "algorithm"}.issubset(
        fixture_tag_ids
    )

    mapped_topic_tags = {
        tag_id
        for mapping in mappings["mappings"]
        for tag_id in mapping.get("topicTags", [])
    }
    assert {"transaction", "sql", "security", "network", "algorithm"}.issubset(
        mapped_topic_tags
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
