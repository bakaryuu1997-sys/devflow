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


def test_v109_conflict_report_exposes_digest_lock():
    snapshot = _snapshot()
    report = client.post(
        "/api/release-governance/v10-9-restore-conflict-report?profile_id=core-risk", json=snapshot
    ).json()
    assert report["version"] == "10.9"
    assert report["ready"] is True
    assert report["snapshot_digest_lock_required"] == snapshot["snapshot_digest"]
    assert report["status"] == "No restore conflict detected"


def test_v109_detects_snapshot_row_digest_conflict():
    snapshot = _snapshot()
    snapshot["snapshot"]["tables"]["projects"][0]["description"] = "changed stale snapshot"
    report = client.post(
        "/api/release-governance/v10-9-restore-conflict-report?profile_id=core-risk", json=snapshot
    ).json()
    assert report["status"] == "Conflict detected"
    assert any(item["type"] == "row_digest_delta" for item in report["conflicts"])


def test_v109_blocks_missing_lock_then_restores_with_digest_audit():
    snapshot = _snapshot()
    phrase = "RESTORE%20DEMO%20PROFILE:%20core-risk"
    blocked = client.post(
        f"/api/release-governance/v10-9-execute-guarded-manual-restore?profile_id=core-risk&restore_approval={phrase}",
        json=snapshot,
    ).json()
    assert blocked["ready"] is False
    assert blocked["status"] == "Snapshot digest lock required"
    locked = client.post(
        f"/api/release-governance/v10-9-execute-guarded-manual-restore?profile_id=core-risk&restore_approval={phrase}&snapshot_digest_lock={snapshot['snapshot_digest']}&operator_name=tester",
        json=snapshot,
    ).json()
    assert locked["version"] == "10.9"
    assert locked["ready"] is True
    assert locked["snapshot_digest_lock"] == snapshot["snapshot_digest"]
    audit = client.get("/api/release-governance/v10-9-restore-digest-lock-audit-trail?profile_id=core-risk").json()
    assert audit["audit_events"]
    assert audit["audit_events"][0]["operator_name"] == "tester"


def test_v109_routes_ui_docs_and_cli_export(tmp_path):
    package = client.get("/api/release-governance/v10-9-operator-restore-conflict-package?profile_id=core-risk").json()
    assert "Operator Restore Conflict Package" in package["content"]
    assert "routes_v109" in " ".join(wired_route_modules())
    assert "governance_v109_ui.js" in Path("static/index.html").read_text(encoding="utf-8")
    assert Path("docs/V10_9_RESTORE_CONFLICT_DIGEST_LOCK.md").exists()
    out = tmp_path / "restore.md"
    result = subprocess.run(
        [sys.executable, "scripts/export_v10_9_restore_conflict_package.py", str(out)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "v10.9 Operator Restore Conflict Package" in out.read_text(encoding="utf-8")
