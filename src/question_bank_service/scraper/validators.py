from html.parser import HTMLParser


def validate_question_detail(
    *,
    expected_choice_count: int,
    choices: list[dict[str, str]],
    html_fragments: list[str],
    required_notation: list[str],
) -> list[dict[str, str]]:
    failures: list[dict[str, str]] = []

    if len(choices) != expected_choice_count:
        failures.append(
            {
                "code": "choice_count_mismatch",
                "message": f"Expected {expected_choice_count} choices but found {len(choices)}",
            }
        )

    if any(not _has_balanced_tags(fragment) for fragment in html_fragments):
        failures.append(
            {
                "code": "html_unbalanced",
                "message": "HTML fragment has unbalanced tags",
            }
        )

    searchable_text = "\n".join(
        [*(choice.get("text", "") for choice in choices), *html_fragments]
    )
    for notation in required_notation:
        if notation not in searchable_text:
            failures.append(
                {
                    "code": "notation_missing",
                    "message": f"Required notation was not preserved: {notation}",
                }
            )

    return failures


def _has_balanced_tags(fragment: str) -> bool:
    parser = _BalanceParser()
    try:
        parser.feed(fragment)
        parser.close()
    except ValueError:
        return False
    return not parser.open_tags


class _BalanceParser(HTMLParser):
    void_tags = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self) -> None:
        super().__init__()
        self.open_tags: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in self.void_tags:
            self.open_tags.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if not self.open_tags or self.open_tags[-1] != tag:
            raise ValueError(tag)
        self.open_tags.pop()
