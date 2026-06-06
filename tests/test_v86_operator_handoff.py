from pathlib import Path
import sqlite3
import subprocess
import sys

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_v86_production_upgrade_runbook_endpoint_is_wired():
    data = client.get("/api/release-governance/production-upgrade-runbook").json()
    assert data["version"] == "8.6"
    assert data["mode"] == "production-upgrade-runbook"
    assert data["approval_phrase"] == "I_APPROVE_PRODUCTION_MIGRATION"
    assert any(phase["name"].startswith("1.") for phase in data["phases"])
    assert "Production Upgrade Runbook" in data["content"]


def test_v86_operator_handoff_package_endpoint_is_wired():
    data = client.get("/api/release-governance/operator-handoff-package").json()
    assert data["version"] == "8.6"
    assert data["mode"] == "operator-handoff-package"
    assert "RUNBOOK.md" in data["required_files"]
    assert data["manifest"]["approval_phrase_required"] == "I_APPROVE_PRODUCTION_MIGRATION"
    assert "Operator Handoff Package" in data["content"]


def test_v86_runbook_cli_exports_markdown(tmp_path):
    db_path = tmp_path / "legacy.db"
    out_path = tmp_path / "RUNBOOK.md"
    create_legacy_database(db_path)
    result = subprocess.run([
        sys.executable,
        "scripts/export_upgrade_runbook.py",
        str(db_path),
        str(out_path),
    ], text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    content = out_path.read_text(encoding="utf-8")
    assert "v8.6 production upgrade runbook" in content.lower()
    assert "I_APPROVE_PRODUCTION_MIGRATION" in content


def test_v86_operator_handoff_cli_writes_package_and_static_ui_is_wired(tmp_path):
    db_path = tmp_path / "legacy.db"
    out_dir = tmp_path / "handoff"
    create_legacy_database(db_path)
    result = subprocess.run([
        sys.executable,
        "scripts/operator_handoff_package.py",
        str(db_path),
        str(out_dir),
    ], text=True, capture_output=True, check=False)
    index_html = Path("static/index.html").read_text(encoding="utf-8")
    routes_py = Path("app/routes.py").read_text(encoding="utf-8")
    ui_js = Path("static/migration_handoff_ui.js").read_text(encoding="utf-8")
    assert result.returncode == 0, result.stdout + result.stderr
    assert (out_dir / "RUNBOOK.md").exists()
    assert (out_dir / "OPERATOR_HANDOFF.md").exists()
    assert "Upgrade Runbook" in index_html
    assert "Operator Handoff" in index_html
    assert "routes_v86" in routes_py
    assert "production-upgrade-runbook" in ui_js


def create_legacy_database(path: Path) -> None:
    con = sqlite3.connect(path)
    try:
        con.execute("CREATE TABLE release_signoffs (id INTEGER PRIMARY KEY, snapshot TEXT DEFAULT '')")
        con.execute("CREATE TABLE release_learning_items (id INTEGER PRIMARY KEY, status TEXT DEFAULT '')")
        con.commit()
    finally:
        con.close()
