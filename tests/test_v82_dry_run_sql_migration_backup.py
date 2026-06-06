from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_v82_dry_run_sql_migration_is_safe_and_exportable():
    data = client.get("/api/release-governance/dry-run-sql-migration").json()

    assert data["version"] == "8.2"
    assert data["mode"] == "dry-run"
    assert data["will_apply_changes"] is False
    assert data["status"] in {"No SQL Needed", "SQL Ready"}
    assert "Dry-run SQL Migration" in data["content"]
    assert all(row["destructive"] is False for row in data["statements"])


def test_v82_backup_checklist_contains_verify_and_rollback_steps():
    data = client.get("/api/release-governance/backup-checklist").json()

    assert data["version"] == "8.2"
    assert data["backup_required"] is True
    assert any("Copy the SQLite file" in step for step in data["checklist"])
    assert any("migration_check.py" in step for step in data["verification_steps"])
    assert any("Restore" in step for step in data["rollback_steps"])
    assert "Backup Checklist" in data["content"]


def test_v82_static_ui_routes_and_cli_generator_exist():
    index_html = open("static/index.html", encoding="utf-8").read()
    ui_js = open("static/migration_sql_ui.js", encoding="utf-8").read()
    routes_py = open("app/routes.py", encoding="utf-8").read()
    script_py = open("scripts/dry_run_migration_sql.py", encoding="utf-8").read()

    assert "Dry-run SQL" in index_html
    assert "Backup Checklist" in index_html
    assert "dry-run-sql-migration" in ui_js
    assert "backup-checklist" in ui_js
    assert "routes_v82" in routes_py
    assert "CREATE TABLE IF NOT EXISTS scope_decision_audits" in script_py
