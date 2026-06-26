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


def test_parse_question_detail_html_preserves_current_fe_siken_images() -> None:
    html = """
    <div id="mondai">
      X□Yの真理値表はどれか。
      <div class="img_margin">
        <img src="img/01.png" width="479" height="117" alt="01.png/image-size:479×117">
      </div>
    </div>
    <ul class="selectList col2">
      <li>
        <button class="selectBtn">ア</button>
        <span>
          <img src="img/01a.png" width="140" height="138" alt="01a.png/image-size:140×138">
        </span>
      </li>
      <li>
        <button class="selectBtn">イ</button>
        <span>
          <img src="img/01i.png" width="140" height="138" alt="01i.png/image-size:140×138">
        </span>
      </li>
      <li>
        <button class="selectBtn" id="t">ウ</button>
        <span>
          <img src="img/01u.png" width="140" height="139" alt="01u.png/image-size:140×139">
        </span>
      </li>
      <li>
        <button class="selectBtn">エ</button>
        <span>
          <img src="img/01e.png" width="140" height="139" alt="01e.png/image-size:140×139">
        </span>
      </li>
    </ul>
    <span id="answerChar">ウ</span>
    <div id="kaisetsu">
      真理値表の演算結果。
      <div class="img_margin">
        <img src="img/01_1.png" width="435" height="108" alt="01_1.png/image-size:435×108">
      </div>
    </div>
    """

    detail = parse_question_detail_html(
        html,
        question_url="https://www.fe-siken.com/kakomon/06_haru/a1.html",
    )

    assert detail.question_text == (
        "X□Yの真理値表はどれか。\n\n"
        "![01.png/image-size:479×117](/assets/fe-siken/06_haru/a1/01.png)"
    )
    assert detail.choices == [
        {
            "label": "ア",
            "text": "![01a.png/image-size:140×138](/assets/fe-siken/06_haru/a1/01a.png)",
        },
        {
            "label": "イ",
            "text": "![01i.png/image-size:140×138](/assets/fe-siken/06_haru/a1/01i.png)",
        },
        {
            "label": "ウ",
            "text": "![01u.png/image-size:140×139](/assets/fe-siken/06_haru/a1/01u.png)",
        },
        {
            "label": "エ",
            "text": "![01e.png/image-size:140×139](/assets/fe-siken/06_haru/a1/01e.png)",
        },
    ]
    assert detail.answer == "ウ"
    assert detail.explanation == (
        "真理値表の演算結果。\n\n"
        "![01_1.png/image-size:435×108](/assets/fe-siken/06_haru/a1/01_1.png)"
    )
    assert detail.has_images is True
    assert detail.images == [
        {
            "src": "img/01.png",
            "alt": "01.png/image-size:479×117",
            "section": "question",
            "publicPath": "/assets/fe-siken/06_haru/a1/01.png",
        },
        {
            "src": "img/01a.png",
            "alt": "01a.png/image-size:140×138",
            "section": "choice",
            "choiceLabel": "ア",
            "publicPath": "/assets/fe-siken/06_haru/a1/01a.png",
        },
        {
            "src": "img/01i.png",
            "alt": "01i.png/image-size:140×138",
            "section": "choice",
            "choiceLabel": "イ",
            "publicPath": "/assets/fe-siken/06_haru/a1/01i.png",
        },
        {
            "src": "img/01u.png",
            "alt": "01u.png/image-size:140×139",
            "section": "choice",
            "choiceLabel": "ウ",
            "publicPath": "/assets/fe-siken/06_haru/a1/01u.png",
        },
        {
            "src": "img/01e.png",
            "alt": "01e.png/image-size:140×139",
            "section": "choice",
            "choiceLabel": "エ",
            "publicPath": "/assets/fe-siken/06_haru/a1/01e.png",
        },
        {
            "src": "img/01_1.png",
            "alt": "01_1.png/image-size:435×108",
            "section": "explanation",
            "publicPath": "/assets/fe-siken/06_haru/a1/01_1.png",
        },
    ]


def test_parse_question_detail_html_preserves_fe_siken_fraction_choices() -> None:
    html = """
    <div id="mondai">処理時間は何倍になるか。</div>
    <ul class="selectList col4">
      <li>
        <button class="selectBtn">ア</button>
        <span id="select_a"><span class="frac"><span>1</span>32</span></span>
      </li>
      <li>
        <button class="selectBtn">イ</button>
        <span id="select_i"><span class="frac"><span>1</span>2</span></span>
      </li>
      <li><button class="selectBtn" id="t">ウ</button><span id="select_u">2</span></li>
      <li><button class="selectBtn">エ</button><span id="select_e">8</span></li>
    </ul>
    <span id="answerChar">ウ</span>
    <div id="kaisetsu">解説</div>
    """

    detail = parse_question_detail_html(
        html,
        question_url="https://www.fe-siken.com/kakomon/04_menjo/q12.html",
    )

    assert detail.choices == [
        {"label": "ア", "text": "1/32"},
        {"label": "イ", "text": "1/2"},
        {"label": "ウ", "text": "2"},
        {"label": "エ", "text": "8"},
    ]


def test_parse_question_detail_html_preserves_menjo_q9_fraction_choices() -> None:
    html = """
    <div id="mondai">平均比較回数を表す式はどれか。</div>
    <ul class="selectList col4">
      <li>
        <button class="selectBtn">ア</button>
        <span id="select_a">m＋<span class="frac"><span>n</span>m</span></span>
      </li>
      <li>
        <button class="selectBtn" id="t">イ</button>
        <span id="select_i">
          <span class="frac"><span>m</span>2</span>＋<span class="frac"><span>n</span>2m</span>
        </span>
      </li>
      <li>
        <button class="selectBtn">ウ</button>
        <span id="select_u"><span class="frac"><span>n</span>m</span></span>
      </li>
      <li>
        <button class="selectBtn">エ</button>
        <span id="select_e"><span class="frac"><span>n</span>2m</span></span>
      </li>
    </ul>
    <span id="answerChar">イ</span>
    <div id="kaisetsu">
      合計は<span class="frac"><span>m</span>2</span>＋<span class="frac"><span>n</span>2m</span>。
    </div>
    """

    detail = parse_question_detail_html(
        html,
        question_url="https://www.fe-siken.com/kakomon/04_menjo/q9.html",
    )

    assert detail.choices == [
        {"label": "ア", "text": "m＋n/m"},
        {"label": "イ", "text": "m/2＋n/2m"},
        {"label": "ウ", "text": "n/m"},
        {"label": "エ", "text": "n/2m"},
    ]
    assert detail.explanation == "合計はm/2＋n/2m。"
