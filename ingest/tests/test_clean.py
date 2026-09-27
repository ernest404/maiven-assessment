from clean import clean_text


def test_strips_html_and_unescapes():
    assert clean_text("SO<INF>2</INF> &amp; emissions") == "SO2 & emissions"


def test_collapses_whitespace_and_strips():
    assert clean_text("  hello   \n\n  world  ") == "hello world"


def test_handles_nbsp():
    assert clean_text("Part\xa0one\n\ntwo") == "Part one two"


def test_none_returns_none():
    assert clean_text(None) is None


def test_empty_returns_none():
    assert clean_text("   ") is None
