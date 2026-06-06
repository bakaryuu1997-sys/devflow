from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_v84_safe_copy_migration_apply_endpoint_never_touches_original():
    data = client.get("/api/release-governance/safe-copy-migration-apply").json()

    assert data["version"] == "8.4"
    assert data["mode"] == "safe-copy-migration-apply"
    assert data["will_modify_original_database"] is False
    assert "safe_copy_migration_apply.py" in "\n".join(data["commands"])
    assert "Safe Migration Apply on Copied Database" in data["content"]


def test_v84_rollback_drill_endpoint_has_clear_success_criteria():
    data = client.get("/api/release-governance/rollback-drill-automation").json()

    assert data["version"] == "8.4"
    assert data["mode"] == "rollback-drill-automation"
    assert data["will_modify_original_database"] is False
    assert any("checksum" in item.lower() for item in data["success_criteria"])
    assert "Rollback Drill Automation" in data["content"]


def test_v84_cli_safe_copy_apply_and_rollback_drill(tmp_path):
    source = tmp_path / "legacy.db"
    copy = tmp_path / "legacy_copy.db"
    create_legacy_database(source)
    before = source.read_bytes()

    apply_result = subprocess.run(
        [sys.executable, "scripts/safe_copy_migration_apply.py", str(source), str(copy)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert apply_result.returncode == 0, apply_result.stdout + apply_result.stderr
    assert source.read_bytes() == before
    assert copy.exists()
    assert_has_column(copy, "release_signoffs", "snapshot_json")
    assert_has_column(copy, "release_learning_items", "owner")
    assert_has_table(copy, "scope_decision_audits")

    drill_source = tmp_path / "drill.db"
    shutil.copy2(source, drill_source)
    rollback_result = subprocess.run(
        [sys.executable, "scripts/rollback_drill.py", str(drill_source)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert rollback_result.returncode == 0, rollback_result.stdout + rollback_result.stderr
    assert "ROLLBACK DRILL PASSED" in rollback_result.stdout


def test_v84_static_ui_and_routes_are_wired():
    index_html = Path("static/index.html").read_text(encoding="utf-8")
    ui_js = Path("static/migration_apply_ui.js").read_text(encoding="utf-8")
    routes_py = Path("app/routes.py").read_text(encoding="utf-8")

    assert "Safe Copy Apply" in index_html
    assert "Rollback Drill" in index_html
    assert "safe-copy-migration-apply" in ui_js
    assert "rollback-drill-automation" in ui_js
    assert "routes_v84" in routes_py


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
