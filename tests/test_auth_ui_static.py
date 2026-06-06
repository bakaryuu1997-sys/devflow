from pathlib import Path


STATIC_ROOT = Path(__file__).resolve().parents[1] / "static"


def test_auth_toggle_targets_existing_button_id():
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")

    assert 'id="authButton"' in html
    assert 'getElementById("authButton")' in html
    assert 'authSubmitBtn' not in html


def test_login_form_does_not_prefill_demo_password():
    html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")

    assert 'id="password" type="password" placeholder="Enter password"' in html
    assert 'id="password" type="password" value="password123"' not in html


def test_demo_credentials_are_user_triggered_only():
    app_js = (STATIC_ROOT / "app.js").read_text(encoding="utf-8")
    flow_js = (STATIC_ROOT / "flow.js").read_text(encoding="utf-8")

    assert "function fillDemoLogin()" in app_js
    assert 'password.value = "password123"' in app_js
    assert 'password123' in flow_js
