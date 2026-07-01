from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def test_v81_local_migration_check_reports_current_schema_ready():
    data = client.get("/api/release-governance/local-migration-check").json()

    assert data["version"] == "8.1"
    assert data["status"] == "Ready"
    assert data["safe_to_upgrade"] is True
    assert any(row["table"] == "release_signoffs" for row in data["required_schema"])
    assert any(row["table"] == "scope_decision_audits" for row in data["required_schema"])
    assert "Local Database Migration Check" in data["content"]


def test_v81_upgrade_safety_report_is_exportable():
    data = client.get("/api/release-governance/upgrade-safety-report").json()

    assert data["version"] == "8.1"
    assert data["status"] == "Upgrade Safe"
    assert data["risk_score"] == 0
    assert data["safe_to_upgrade"] is True
    assert data["must_fix_before_upgrade"] == []
    assert "Upgrade Safety Report" in data["content"]


def test_v81_static_ui_routes_and_cli_checker_exist():
    index_html = open("static/index.html", encoding="utf-8").read()
    ui_js = open("static/migration_checker_ui.js", encoding="utf-8").read()
    routes_py = " ".join(wired_route_modules())
    script_py = open("scripts/migration_check.py", encoding="utf-8").read()

    assert "Migration Check" in index_html
    assert "Upgrade Safety" in index_html
    assert "local-migration-check" in ui_js
    assert "upgrade-safety-report" in ui_js
    assert "routes_v81" in routes_py
    assert "REQUIRED_SCHEMA" in script_py
