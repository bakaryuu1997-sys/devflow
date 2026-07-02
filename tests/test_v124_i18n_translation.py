from pathlib import Path


def test_i18n_file_exists():
    i18n_path = Path("static/i18n.js")
    assert i18n_path.exists()
    content = i18n_path.read_text(encoding="utf-8")
    assert "TRANSLATIONS" in content
    assert "vi:" in content
    assert "en:" in content
    assert "sidebar_title" in content


def test_phrase_dictionary_and_default_vietnamese():
    content = Path("static/i18n.js").read_text(encoding="utf-8")

    # Phrase dictionaries + text-node translator power full-page Vietnamese
    # for strings that do not carry a data-i18n attribute.
    assert "PHRASE_MAP" in content
    assert "VNN_SUFFIX" in content
    assert "function translateTextNodes" in content
    # A few representative translations are present.
    assert "Mẫu lỗi" in content  # Bug Patterns
    assert "Cổng Chữ ký" in content  # Signature gates
    # The app defaults to Vietnamese.
    assert 'localStorage.getItem("devflow_lang") || "vi"' in content


def test_index_html_includes_i18n():
    html_path = Path("static/index.html")
    assert html_path.exists()
    content = html_path.read_text(encoding="utf-8")

    # Verify script linking
    assert "static/i18n.js" in content

    # Verify key data-i18n translation attributes exist
    assert 'data-i18n="topbar_eyebrow"' in content
    assert 'data-i18n="topbar_title"' in content
    assert 'data-i18n="login_title"' in content
    assert 'data-i18n="sidebar_title"' in content
    assert 'data-i18n="step1_title"' in content
    assert "langBtn" in content
