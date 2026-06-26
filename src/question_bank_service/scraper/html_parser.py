from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin, urlparse

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
    images: list[dict[str, Any]]
    has_images: bool


def parse_question_detail_html(html: str, *, question_url: str) -> ParsedQuestionDetail:
    soup = BeautifulSoup(html, "html.parser")
    question = _required_select_one(soup, ["#question", "#mondai"], "question")
    explanation = _required_select_one(soup, ["#explanation", "#kaisetsu"], "explanation")
    choices = _parse_choices(soup, question_url=question_url)

    images = [
        *_extract_images(question, section="question", question_url=question_url),
        *[
            image
            for choice in choices
            for image in choice.pop("_images", [])
        ],
        *_extract_images(explanation, section="explanation", question_url=question_url),
    ]
    return ParsedQuestionDetail(
        question_url=question_url,
        question_text=_normalize_text(_text_content(question, question_url=question_url)),
        choices=choices,
        answer=_normalize_text(
            _text_content(
                _required_select_one(soup, ["#answer", "#answerChar"], "answer"),
                question_url=question_url,
            )
        ),
        explanation=_normalize_text(_text_content(explanation, question_url=question_url)),
        images=images,
        has_images=bool(images),
    )


def _parse_choices(soup: BeautifulSoup, *, question_url: str) -> list[dict[str, Any]]:
    choice_items = soup.select(".choices li") or soup.select(".selectList li")
    if not choice_items:
        raise HtmlParseError("choices were not found")

    choices: list[dict[str, Any]] = []
    for item in choice_items:
        label_node = item.select_one(".choice-label") or item.select_one(".selectBtn")
        if label_node is None:
            raise HtmlParseError("choice label was not found")
        label = _normalize_text(_text_content(label_node, question_url=question_url))
        label_node.extract()
        choices.append(
            {
                "label": label,
                "text": _normalize_text(_text_content(item, question_url=question_url)),
                "_images": _extract_images(
                    item,
                    section="choice",
                    question_url=question_url,
                    choice_label=label,
                ),
            }
        )
    return choices


def _extract_images(
    root: Tag,
    *,
    section: str | None = None,
    question_url: str | None = None,
    choice_label: str | None = None,
) -> list[dict[str, Any]]:
    images: list[dict[str, Any]] = []
    for image in root.select("img"):
        src = image.get("src")
        if not isinstance(src, str) or not src:
            continue
        alt = image.get("alt")
        metadata: dict[str, Any] = {"src": src, "alt": alt if isinstance(alt, str) else ""}
        public_path = _public_asset_path(src, question_url=question_url)
        if public_path is not None:
            if section is not None:
                metadata["section"] = section
            if choice_label is not None:
                metadata["choiceLabel"] = choice_label
            metadata["publicPath"] = public_path
        images.append(metadata)
    return images


def _required_select_one(soup: BeautifulSoup | Tag, selectors: list[str], name: str) -> Tag:
    for selector in selectors:
        node = soup.select_one(selector)
        if isinstance(node, Tag):
            return node
    raise HtmlParseError(f"{name} section was not found")


def _text_content(node: Tag | NavigableString, *, question_url: str | None) -> str:
    if isinstance(node, NavigableString):
        return str(node)

    if _is_fraction(node):
        return _fraction_text(node, question_url=question_url)
    if _is_overline(node):
        return f"¬{_children_text(node, question_url=question_url)}"
    if node.name == "sup":
        return f"^{_children_text(node, question_url=question_url)}"
    if node.name == "sub":
        return f"_{_children_text(node, question_url=question_url)}"
    if node.name in {"script", "style"}:
        return ""
    if node.name == "img":
        markdown = _image_markdown(node, question_url=question_url)
        return f"\n\n{markdown}\n\n" if markdown is not None else ""
    if node.name == "br":
        return "\n"

    return _children_text(node, question_url=question_url)


def _children_text(node: Tag, *, question_url: str | None) -> str:
    return "".join(_text_content(child, question_url=question_url) for child in node.children)


def _is_overline(node: Tag) -> bool:
    classes = node.get("class", [])
    style = node.get("style", "")
    class_values = classes if isinstance(classes, list) else [classes]
    has_overline_class = any("overline" in str(value).lower() for value in class_values)
    has_overline_style = isinstance(style, str) and "overline" in style.lower()
    return has_overline_class or has_overline_style


def _is_fraction(node: Tag) -> bool:
    classes = node.get("class", [])
    class_values = classes if isinstance(classes, list) else [classes]
    return any(str(value).lower() == "frac" for value in class_values)


def _fraction_text(node: Tag, *, question_url: str | None) -> str:
    children = list(node.children)
    if len(children) < 2:
        return _children_text(node, question_url=question_url)

    numerator = _text_content(children[0], question_url=question_url)
    denominator = "".join(
        _text_content(child, question_url=question_url) for child in children[1:]
    )
    numerator = _normalize_inline_text(numerator)
    denominator = _normalize_inline_text(denominator)
    if not numerator or not denominator:
        return _children_text(node, question_url=question_url)
    return f"{numerator}/{denominator}"


def _normalize_text(value: str) -> str:
    paragraphs = []
    for paragraph in value.replace("\r\n", "\n").replace("\r", "\n").split("\n\n"):
        normalized = " ".join(paragraph.split()).strip()
        if normalized:
            paragraphs.append(normalized)
    return "\n\n".join(paragraphs)


def _normalize_inline_text(value: str) -> str:
    return " ".join(value.split()).strip()


def _image_markdown(node: Tag, *, question_url: str | None) -> str | None:
    src = node.get("src")
    if not isinstance(src, str) or not src:
        return None
    public_path = _public_asset_path(src, question_url=question_url)
    if public_path is None:
        return None
    alt = node.get("alt")
    return f"![{alt if isinstance(alt, str) else ''}]({public_path})"


def _public_asset_path(src: str, *, question_url: str | None) -> str | None:
    if not question_url:
        return None

    absolute = urlparse(urljoin(question_url, src))
    parts = [part for part in absolute.path.split("/") if part]
    if len(parts) < 4 or parts[0] != "kakomon" or parts[-2] != "img":
        return None

    question_parts = [part for part in urlparse(question_url).path.split("/") if part]
    if len(question_parts) < 3 or question_parts[0] != "kakomon":
        return None

    exam = question_parts[1]
    question_id = question_parts[2].removesuffix(".html")
    return f"/assets/fe-siken/{exam}/{question_id}/{parts[-1]}"
