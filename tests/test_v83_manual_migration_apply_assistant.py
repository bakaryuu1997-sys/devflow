from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def test_v83_manual_migration_apply_assistant_is_safe_and_copyable():
    data = client.get("/api/release-governance/manual-migration-apply-assistant").json()

    assert data["version"] == "8.3"
    assert data["mode"] == "manual-apply-assistant"
    assert data["will_apply_changes"] is False
    assert "BEGIN TRANSACTION" in data["sql_script"] or "No SQL needed" in data["sql_script"]
    assert any("copied database" in step.lower() for step in data["manual_apply_steps"])
    assert "Manual Migration Apply Assistant" in data["content"]


def test_v83_post_migration_verification_snapshot_reports_remaining_actions():
    data = client.get("/api/release-governance/post-migration-verification-snapshot").json()

    assert data["version"] == "8.3"
    assert data["mode"] == "post-migration-verification"
    assert data["status"] in {"Verified", "Follow-up Needed"}
    assert isinstance(data["verified_schema"], list)
    assert isinstance(data["remaining_actions"], list)
    assert "Post-migration Verification Snapshot" in data["content"]


def test_v83_static_ui_routes_and_cli_helpers_exist():
    index_html = open("static/index.html", encoding="utf-8").read()
    ui_js = open("static/migration_apply_ui.js", encoding="utf-8").read()
    routes_py = " ".join(wired_route_modules())
    apply_script = open("scripts/manual_migration_apply_assistant.py", encoding="utf-8").read()
    verify_script = open("scripts/post_migration_verify.py", encoding="utf-8").read()

    assert "Apply Assistant" in index_html
    assert "Post-migration Verify" in index_html
    assert "manual-migration-apply-assistant" in ui_js
    assert "post-migration-verification-snapshot" in ui_js
    assert "routes_v83" in routes_py
    assert "This script does not apply SQL automatically" in apply_script
    assert "Remaining SQL statements" in verify_script
