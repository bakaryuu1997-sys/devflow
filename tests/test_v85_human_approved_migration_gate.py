import sqlite3
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def test_v85_real_migration_gate_endpoint_requires_human_approval():
    data = client.get("/api/release-governance/human-approved-real-migration-gate").json()
    assert data["version"] == "8.5"
    assert data["mode"] == "human-approved-real-migration-gate"
    assert data["will_modify_original_database"] is True
    assert data["approval_phrase"] == "I_APPROVE_PRODUCTION_MIGRATION"
    assert "real_migration_gate.py" in "\n".join(data["approval_commands"])
    assert "Human-approved Real Migration Gate" in data["content"]


def test_v85_final_production_upgrade_checklist_endpoint_is_wired():
    data = client.get("/api/release-governance/final-production-upgrade-checklist").json()
    assert data["version"] == "8.5"
    assert data["mode"] == "final-production-upgrade-checklist"
    assert data["approval_phrase"] == "I_APPROVE_PRODUCTION_MIGRATION"
    assert any(section["name"] == "Rollback readiness" for section in data["sections"])
    assert "Final Production Upgrade Checklist" in data["content"]


def test_v85_real_migration_gate_cli_blocks_without_exact_approval(tmp_path):
    db_path = tmp_path / "legacy.db"
    create_legacy_database(db_path)
    before = db_path.read_bytes()
    result = subprocess.run(
        [sys.executable, "scripts/real_migration_gate.py", str(db_path)], text=True, capture_output=True, check=False
    )
    assert result.returncode == 3
    assert "human approval required" in result.stdout.lower()
    assert db_path.read_bytes() == before
    assert not list(tmp_path.glob("*.v8_5_prod_backup_*.db"))


def test_v85_real_migration_gate_cli_applies_after_approval_and_creates_backup(tmp_path):
    db_path = tmp_path / "legacy.db"
    create_legacy_database(db_path)
    result = subprocess.run(
        [
            sys.executable,
            "scripts/real_migration_gate.py",
            str(db_path),
            "--approve",
            "I_APPROVE_PRODUCTION_MIGRATION",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PRODUCTION MIGRATION VERIFIED" in result.stdout
    assert list(tmp_path.glob("legacy.v8_5_prod_backup_*.db"))
    assert_has_column(db_path, "release_signoffs", "snapshot_json")
    assert_has_column(db_path, "release_learning_items", "owner")
    assert_has_table(db_path, "scope_decision_audits")


def test_v85_production_upgrade_checklist_cli_and_static_ui_are_wired(tmp_path):
    db_path = tmp_path / "legacy.db"
    create_legacy_database(db_path)
    result = subprocess.run(
        [sys.executable, "scripts/production_upgrade_checklist.py", str(db_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    index_html = Path("static/index.html").read_text(encoding="utf-8")
    ui_js = Path("static/migration_apply_ui.js").read_text(encoding="utf-8")
    routes_py = " ".join(wired_route_modules())
    assert result.returncode == 1
    assert "final production upgrade checklist" in result.stdout.lower()
    assert "Real Migration Gate" in index_html
    assert "Production Checklist" in index_html
    assert "human-approved-real-migration-gate" in ui_js
    assert "routes_v85" in routes_py


def create_legacy_database(path: Path) -> None:
    con = sqlite3.connect(path)
    try:
        con.execute("CREATE TABLE release_signoffs (id INTEGER PRIMARY KEY, snapshot TEXT DEFAULT '')")
        con.execute("CREATE TABLE release_learning_items (id INTEGER PRIMARY KEY, status TEXT DEFAULT '')")
        con.commit()
    finally:
        con.close()


def assert_has_column(path: Path, table: str, column: str) -> None:
    con = sqlite3.connect(path)
    try:
        columns = {row[1] for row in con.execute(f"PRAGMA table_info({table})")}
    finally:
        con.close()
    assert column in columns


def assert_has_table(path: Path, table: str) -> None:
    con = sqlite3.connect(path)
    try:
        tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        con.close()
    assert table in tables
