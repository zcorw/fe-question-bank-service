from question_bank_service.daily_practice import generate_daily_practice_markdown


def test_generate_daily_practice_markdown_uses_runtime_client_batch_details() -> None:
    client = FakeRuntimeClient()

    markdown = generate_daily_practice_markdown(
        client,
        title="今日の練習",
        category="基礎理論",
        limit=2,
    )

    assert client.candidate_filters == {"category": "基礎理論", "limit": 2}
    assert client.detail_urls == ["https://example.test/q1", "https://example.test/q2"]
    assert "# 今日の練習" in markdown
    assert "## 1. 問1" in markdown
    assert "2^5 と ¬x" in markdown
    assert "- ア. 32" in markdown
    assert "## 2. 問2" in markdown
    assert "SQL の問題" in markdown
    assert "正解" not in markdown
    assert "解説" not in markdown


class FakeRuntimeClient:
    def __init__(self) -> None:
        self.candidate_filters: dict[str, object] | None = None
        self.detail_urls: list[str] | None = None

    def find_candidates(self, *, category: str | None, limit: int) -> list[dict[str, object]]:
        self.candidate_filters = {"category": category, "limit": limit}
        return [
            {"questionNo": "問1", "questionUrl": "https://example.test/q1"},
            {"questionNo": "問2", "questionUrl": "https://example.test/q2"},
        ]

    def get_details_by_urls(
        self,
        urls: list[str],
        *,
        include_answer: bool,
        include_explanation: bool,
    ) -> list[dict[str, object]]:
        self.detail_urls = urls
        assert include_answer is False
        assert include_explanation is False
        return [
            {
                "questionUrl": "https://example.test/q1",
                "questionText": "2^5 と ¬x",
                "choices": [{"label": "ア", "text": "32"}],
            },
            {
                "questionUrl": "https://example.test/q2",
                "questionText": "SQL の問題",
                "choices": [{"label": "ア", "text": "SELECT"}],
            },
        ]
