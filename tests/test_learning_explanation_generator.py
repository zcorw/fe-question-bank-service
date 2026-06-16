import json

from scripts.populate_learning_explanations import build_learning_explanation


def test_build_learning_explanation_uses_existing_data_without_correct_distractor() -> None:
    payload = build_learning_explanation(
        question_url="https://example.test/q1",
        exam_part="科目A",
        category="データ操作",
        topic="SQL",
        question_text="SQL question",
        choices_json=json.dumps(
            [
                {"label": "ア", "text": "SELECT"},
                {"label": "イ", "text": "UPDATE"},
                {"label": "ウ", "text": "DELETE"},
            ],
            ensure_ascii=False,
        ),
        answer="ア",
        existing_explanation="SELECT文は表からデータを取得するために使用する。",
        has_images=True,
        mapping={"syllabusArea": "database", "topicTags": ["sql"]},
    )

    assert payload["questionUrl"] == "https://example.test/q1"
    assert payload["explanationJa"].startswith("SELECT文は表からデータを取得する")
    assert "図表" in payload["explanationJa"]
    assert payload["knowledgePointJa"] == "SQL"
    assert "database" in payload["examPointJa"]
    assert "sql" in payload["examPointJa"]
    assert "ア" not in payload["distractorExplanationsJa"]
    assert set(payload["distractorExplanationsJa"]) == {"イ", "ウ"}
    assert "https://example.test" not in payload["explanationJa"]


def test_build_learning_explanation_removes_image_paths_from_existing_explanation() -> None:
    payload = build_learning_explanation(
        question_url="https://example.test/q1",
        exam_part="科目A",
        category="データ操作",
        topic="SQL",
        question_text="SQL question",
        choices_json=json.dumps(
            [{"label": "ア", "text": "SELECT"}, {"label": "イ", "text": "UPDATE"}],
            ensure_ascii=False,
        ),
        answer="ア",
        existing_explanation=(
            "SQLの条件を確認する。![06.png](/assets/fe-siken/07_haru/a6/06.png)。"
        ),
        has_images=False,
        mapping={},
    )

    assert "/assets/fe-siken" not in payload["explanationJa"]
    assert "![06.png]" not in payload["explanationJa"]
    assert payload["explanationJa"].startswith("SQLの条件を確認する。")


def test_build_learning_explanation_removes_image_paths_from_choice_text() -> None:
    payload = build_learning_explanation(
        question_url="https://example.test/q1",
        exam_part="科目A",
        category="データ操作",
        topic="SQL",
        question_text="SQL question",
        choices_json=json.dumps(
            [
                {"label": "ア", "text": "SELECT"},
                {"label": "イ", "text": "![choice](/assets/fe-siken/q1.png)"},
            ],
            ensure_ascii=False,
        ),
        answer="ア",
        existing_explanation="SQLの条件を確認する。",
        has_images=False,
        mapping={},
    )

    distractor = payload["distractorExplanationsJa"]["イ"]
    assert "/assets/fe-siken" not in distractor
    assert "![choice]" not in distractor
    assert "画像選択肢" in distractor
