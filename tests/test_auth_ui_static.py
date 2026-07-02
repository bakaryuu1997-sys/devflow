from pathlib import Path

STATIC_ROOT = Path(__file__).resolve().parents[1] / "static"


def read_static(name: str) -> str:
    return (STATIC_ROOT / name).read_text(encoding="utf-8")


def test_governance_ui_ships_as_single_bundle():
    html = read_static("index.html")
    bundle = read_static("governance_bundle.js")

    # The page loads exactly the one governance bundle, not per-version scripts.
    assert "/static/governance_bundle.js" in html
    assert "governance_v10_ui.js" not in html
    assert "governance_v120_ui.js" not in html
    # The bundle still contains every version section and shared renderer.
    assert "renderGenericGovernanceCard" in bundle
    assert "// ==== governance_v10_ui.js ====" in bundle
    assert "// ==== governance_v120_ui.js ====" in bundle


def test_head_has_favicon_and_metadata():
    html = read_static("index.html")

    assert '<link rel="icon" href="/static/favicon.svg"' in html
    assert 'name="description"' in html
    assert 'name="color-scheme"' in html
    assert (STATIC_ROOT / "favicon.svg").exists()


def test_form_inputs_are_labelled_for_accessibility():
    html = read_static("index.html")

    # Login labels are programmatically associated with their inputs.
    assert 'for="email"' in html
    assert 'for="password"' in html
    # Placeholder-only inputs expose an accessible name via aria-label.
    for aria in (
        'id="newProjectName" placeholder="New project name" aria-label=',
        'id="sqlFile" type="file" aria-label=',
        'id="logFile" type="file" aria-label=',
        'id="testFile" type="file" aria-label=',
        'id="apiBefore" type="file" aria-label=',
    ):
        assert aria in html, f"missing accessible label: {aria}"


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
