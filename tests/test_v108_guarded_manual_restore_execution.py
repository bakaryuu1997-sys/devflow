import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def _snapshot():
    client.post("/api/demo/reset")
    client.post("/api/release-governance/v10-4-build-sample-project?profile_id=core-risk")
    return client.get("/api/release-governance/v10-6-rollback-snapshot?profile_id=core-risk").json()


def test_v108_restore_plan_requires_ready_rehearsal_and_second_phrase():
    snapshot = _snapshot()
    plan = client.post("/api/release-governance/v10-8-guarded-restore-plan?profile_id=core-risk", json=snapshot).json()
    assert plan["version"] == "10.8"
    assert plan["ready"] is True
    assert plan["restore_approval_phrase"] == "RESTORE DEMO PROFILE: core-risk"
    assert plan["snapshot_digest"] == snapshot["snapshot_digest"]


def test_v108_blocks_wrong_phrase_then_restores_with_audit():
    snapshot = _snapshot()
    blocked = client.post(
        "/api/release-governance/v10-8-execute-guarded-manual-restore?profile_id=core-risk&restore_approval=RESET%20DEMO%20PROFILE:%20core-risk",
        json=snapshot,
    ).json()
    assert blocked["ready"] is False
    assert blocked["status"] == "Second approval phrase required"
    restored = client.post(
        "/api/release-governance/v10-8-execute-guarded-manual-restore?profile_id=core-risk&restore_approval=RESTORE%20DEMO%20PROFILE:%20core-risk&operator_name=tester",
        json=snapshot,
    ).json()
    assert restored["ready"] is True
    assert restored["status"] == "Restore complete"
    assert restored["restored_records"]["projects"] == 1
    audit = client.get("/api/release-governance/v10-8-restore-audit-trail?profile_id=core-risk").json()
    assert audit["audit_events"]
    assert audit["audit_events"][0]["operator_name"] == "tester"


def test_v108_routes_ui_docs_and_cli_export(tmp_path):
    package = client.get("/api/release-governance/v10-8-operator-restore-execution-package?profile_id=core-risk").json()
    assert "Operator Restore Execution Package" in package["content"]
    assert "routes_v108" in " ".join(wired_route_modules())
    assert "governance_v108_ui.js" in Path("static/index.html").read_text(encoding="utf-8")
    assert Path("docs/V10_8_GUARDED_MANUAL_RESTORE_EXECUTION.md").exists()
    out = tmp_path / "restore.md"
    result = subprocess.run(
        [sys.executable, "scripts/export_v10_8_restore_execution_package.py", str(out)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "v10.8 Operator Restore Execution Package" in out.read_text(encoding="utf-8")
