from dataclasses import dataclass

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag


class HtmlParseError(ValueError):
    """Raised when a question detail page cannot be parsed."""


@dataclass(frozen=True)
class ParsedQuestionDetail:
    question_url: str
    question_text: str
    choices: list[dict[str, str]]
    answer: str
    explanation: str
    images: list[dict[str, str]]
    has_images: bool


def parse_question_detail_html(html: str, *, question_url: str) -> ParsedQuestionDetail:
    soup = BeautifulSoup(html, "html.parser")
    question = _required_select_one(soup, "#question", "question")
    explanation = _required_select_one(soup, "#explanation", "explanation")

    images = _extract_images(question)
    return ParsedQuestionDetail(
        question_url=question_url,
        question_text=_normalize_text(_text_content(question)),
        choices=_parse_choices(soup),
        answer=_normalize_text(_text_content(_required_select_one(soup, "#answer", "answer"))),
        explanation=_normalize_text(_text_content(explanation)),
        images=images,
        has_images=bool(images),
    )


def _parse_choices(soup: BeautifulSoup) -> list[dict[str, str]]:
    choice_items = soup.select(".choices li")
    if not choice_items:
        raise HtmlParseError("choices were not found")

    choices: list[dict[str, str]] = []
    for item in choice_items:
        label_node = item.select_one(".choice-label")
        if label_node is None:
            raise HtmlParseError("choice label was not found")
        label = _normalize_text(_text_content(label_node))
        label_node.extract()
        choices.append({"label": label, "text": _normalize_text(_text_content(item))})
    return choices


def _extract_images(root: Tag) -> list[dict[str, str]]:
    images: list[dict[str, str]] = []
    for image in root.select("img"):
        src = image.get("src")
        if not isinstance(src, str) or not src:
            continue
        alt = image.get("alt")
        images.append({"src": src, "alt": alt if isinstance(alt, str) else ""})
    return images


def _required_select_one(soup: BeautifulSoup | Tag, selector: str, name: str) -> Tag:
    node = soup.select_one(selector)
    if not isinstance(node, Tag):
        raise HtmlParseError(f"{name} section was not found")
    return node


def _text_content(node: Tag | NavigableString) -> str:
    if isinstance(node, NavigableString):
        return str(node)

    if _is_overline(node):
        return f"¬{_children_text(node)}"
    if node.name == "sup":
        return f"^{_children_text(node)}"
    if node.name == "sub":
        return f"_{_children_text(node)}"
    if node.name in {"script", "style", "img"}:
        return ""

    return _children_text(node)


def _children_text(node: Tag) -> str:
    return "".join(_text_content(child) for child in node.children)


def _is_overline(node: Tag) -> bool:
    classes = node.get("class", [])
    style = node.get("style", "")
    class_values = classes if isinstance(classes, list) else [classes]
    has_overline_class = any("overline" in str(value).lower() for value in class_values)
    has_overline_style = isinstance(style, str) and "overline" in style.lower()
    return has_overline_class or has_overline_style


def _normalize_text(value: str) -> str:
    return " ".join(value.split()).strip()
