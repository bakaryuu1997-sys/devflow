from pathlib import Path
import sqlite3
import subprocess
import sys

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_v87_rehearsal_report_endpoint_is_wired():
    data = client.get("/api/release-governance/production-upgrade-rehearsal-report").json()
    assert data["version"] == "8.7"
    assert data["mode"] == "production-upgrade-rehearsal-report"
    assert "rehearsal_score" in data
    assert any(row["name"] == "Rollback drill" for row in data["evidence"])
    assert "Production Upgrade Rehearsal Report" in data["content"]


def test_v87_operator_signoff_endpoint_is_wired():
    data = client.get("/api/release-governance/operator-signoff-checklist").json()
    assert data["version"] == "8.7"
    assert data["mode"] == "operator-signoff-checklist"
    assert data["approval_phrase"] == "I_APPROVE_PRODUCTION_MIGRATION"
    assert any(row["role"] == "Operator" for row in data["required_signoffs"])
    assert "Operator Sign-off Checklist" in data["content"]


def test_v87_rehearsal_cli_exports_markdown(tmp_path):
    db_path = tmp_path / "legacy.db"
    out_path = tmp_path / "REHEARSAL_REPORT.md"
    create_legacy_database(db_path)
    result = subprocess.run([
        sys.executable,
        "scripts/export_rehearsal_report.py",
        str(db_path),
        str(out_path),
    ], text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    content = out_path.read_text(encoding="utf-8")
    assert "v8.7 production upgrade rehearsal report" in content.lower()
    assert "I_APPROVE_PRODUCTION_MIGRATION" in content


def test_v87_operator_signoff_cli_and_static_ui_are_wired(tmp_path):
    db_path = tmp_path / "legacy.db"
    out_path = tmp_path / "OPERATOR_SIGNOFF_CHECKLIST.md"
    create_legacy_database(db_path)
    result = subprocess.run([
        sys.executable,
        "scripts/operator_signoff_checklist.py",
        str(db_path),
        str(out_path),
    ], text=True, capture_output=True, check=False)
    index_html = Path("static/index.html").read_text(encoding="utf-8")
    routes_py = Path("app/routes.py").read_text(encoding="utf-8")
    ui_js = Path("static/migration_rehearsal_ui.js").read_text(encoding="utf-8")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "operator sign-off checklist" in out_path.read_text(encoding="utf-8").lower()
    assert "Rehearsal Report" in index_html
    assert "Operator Sign-off" in index_html
    assert "routes_v87" in routes_py
    assert "production-upgrade-rehearsal-report" in ui_js


def create_legacy_database(path: Path) -> None:
    con = sqlite3.connect(path)
    try:
        con.execute("CREATE TABLE release_signoffs (id INTEGER PRIMARY KEY, snapshot TEXT DEFAULT '')")
        con.execute("CREATE TABLE release_learning_items (id INTEGER PRIMARY KEY, status TEXT DEFAULT '')")
        con.commit()
    finally:
        con.close()
