from question_bank_service.scraper.html_parser import parse_question_detail_html


def test_parse_question_detail_html_preserves_notation_and_nested_choices() -> None:
    html = """
    <html>
      <body>
        <section id="question">
          <p>値 2<sup>5</sup> と H<sub>2</sub>O と <span class="overline">x</span></p>
          <img src="/images/q1.png" alt="図1" />
        </section>
        <ol class="choices">
          <li><span class="choice-label">ア</span><span>2<sup>5</sup></span></li>
          <li><span class="choice-label">イ</span><span>¬<span>y</span> を含む</span></li>
        </ol>
        <section id="answer">ア</section>
        <section id="explanation">
          <p><span class="overline">y</span> を使って説明する。</p>
        </section>
      </body>
    </html>
    """

    detail = parse_question_detail_html(html, question_url="https://example.test/q1")

    assert "2^5" in detail.question_text
    assert "H_2O" in detail.question_text
    assert "¬x" in detail.question_text
    assert detail.choices == [
        {"label": "ア", "text": "2^5"},
        {"label": "イ", "text": "¬y を含む"},
    ]
    assert detail.answer == "ア"
    assert "¬y" in detail.explanation
    assert detail.images == [{"src": "/images/q1.png", "alt": "図1"}]
