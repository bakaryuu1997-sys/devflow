from pathlib import Path

STATIC_ROOT = Path(__file__).resolve().parents[1] / "static"


def read_static(name: str) -> str:
    return (STATIC_ROOT / name).read_text(encoding="utf-8")


def test_auth_toggle_targets_existing_button_id():
    html = read_static("index.html")

    assert 'id="authButton"' in html
    assert 'getElementById("authButton")' in html
    assert "authSubmitBtn" not in html


def test_login_form_does_not_prefill_demo_password():
    html = read_static("index.html")

    assert 'id="password" type="password" placeholder="Enter password"' in html
    assert 'id="password" type="password" value="password123"' not in html


def test_sample_credentials_are_local_qa_only():
    html = read_static("index.html")
    app_js = read_static("app.js")

    assert "Use demo admin" not in html
    assert "Use local sample admin" in html
    assert 'href="/workspace"' in html
    assert 'id="localSampleLogin"' in html
    assert "function fillLocalSampleLogin()" in app_js
    assert "function fillDemoLogin()" in app_js
    assert "Local sample credentials are disabled in production" in app_js
    assert "password.value = LOCAL_SAMPLE_CREDENTIALS.password" in app_js


def test_dashboard_history_copy_avoids_demo_reset_language():
    html = read_static("index.html")
    flow_js = read_static("flow.js")

    assert "Click Reset Demo" not in html
    assert "History appears after login or demo reset" not in html
    assert "Deploy compliance parameters" not in html
    assert "Run Reset Demo" not in flow_js
    assert "initialize the local sample workspace" in flow_js


def test_professional_login_command_center_is_wired():
    html = read_static("index.html")
    css = read_static("professional.css")

    # Command-center login markup is present and hooks the existing auth ids.
    for token in (
        "login-command-center",
        "login-stage",
        "login-proof-grid",
        "production-login-card",
        'id="authModeChip"',
        'id="localSampleHint"',
        "Production control room",
    ):
        assert token in html, f"missing login markup: {token}"

    # The professional stylesheet ships the matching layout primitives.
    for selector in (".app-shell", ".sidebar", ".topbar", ".login-command-center"):
        assert selector in css, f"missing stylesheet rule: {selector}"


def test_workspace_history_has_export_and_empty_state():
    html = read_static("workspace.html")
    workspace_js = read_static("workspace.js")

    assert "Browser-local state" in html
    assert 'onclick="exportWorkspaceHistory()"' in html
    assert "function exportWorkspaceHistory()" in workspace_js
    assert "history-empty" in workspace_js
    assert "browser-local localStorage" in workspace_js
