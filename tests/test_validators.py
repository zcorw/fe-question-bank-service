from question_bank_service.scraper.validators import validate_question_detail


def test_validator_reports_choice_count_mismatch() -> None:
    failures = validate_question_detail(
        expected_choice_count=4,
        choices=[{"label": "ア", "text": "only one"}],
        html_fragments=["<p>ok</p>"],
        required_notation=[],
    )

    assert failures == [
        {
            "code": "choice_count_mismatch",
            "message": "Expected 4 choices but found 1",
        }
    ]


def test_validator_reports_unbalanced_html_tag() -> None:
    failures = validate_question_detail(
        expected_choice_count=1,
        choices=[{"label": "ア", "text": "ok"}],
        html_fragments=["<p><span>broken</p>"],
        required_notation=[],
    )

    assert failures == [
        {
            "code": "html_unbalanced",
            "message": "HTML fragment has unbalanced tags",
        }
    ]


def test_validator_reports_missing_required_notation() -> None:
    failures = validate_question_detail(
        expected_choice_count=1,
        choices=[{"label": "ア", "text": "25"}],
        html_fragments=["<p>25</p>"],
        required_notation=["2^5", "¬x"],
    )

    assert failures == [
        {"code": "notation_missing", "message": "Required notation was not preserved: 2^5"},
        {"code": "notation_missing", "message": "Required notation was not preserved: ¬x"},
    ]
