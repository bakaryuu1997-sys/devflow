import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def test_v106_exports_snapshot_for_built_profile_project():
    client.post("/api/demo/reset")
    client.post("/api/release-governance/v10-4-build-sample-project?profile_id=core-risk")
    snapshot = client.get("/api/release-governance/v10-6-rollback-snapshot?profile_id=core-risk").json()
    assert snapshot["version"] == "10.6"
    assert snapshot["ready"] is True
    assert snapshot["snapshot"]["counts"]["projects"] == 1
    assert snapshot["snapshot"]["counts"]["requirements"] == 1
    assert snapshot["snapshot_digest"]
    assert "Rollback Snapshot Export" in snapshot["content"]


def test_v106_execute_reset_records_audit_and_preserves_approval_gate():
    client.post("/api/demo/reset")
    client.post("/api/release-governance/v10-4-build-sample-project?profile_id=core-risk")
    blocked = client.post("/api/release-governance/v10-6-execute-profile-reset?profile_id=core-risk&approval=wrong").json()
    assert blocked["ready"] is False
    assert blocked["status"] == "Approval phrase required"
    phrase = "RESET DEMO PROFILE: core-risk"
    result = client.post(f"/api/release-governance/v10-6-execute-profile-reset?profile_id=core-risk&approval={phrase}&operator_name=Long").json()
    assert result["version"] == "10.6"
    assert result["status"] == "Reset complete"
    assert result["rollback_snapshot_counts"]["requirements"] == 1
    trail = client.get("/api/release-governance/v10-6-profile-reset-audit-trail?profile_id=core-risk").json()
    assert trail["audit_events"]
    assert trail["audit_events"][0]["before_digest"] == result["rollback_snapshot_digest"]


def test_v106_routes_ui_docs_and_cli_export(tmp_path):
    package = client.get("/api/release-governance/v10-6-operator-rollback-package?profile_id=core-risk").json()
    assert package["ready"] is True
    assert "Operator Rollback Snapshot Package" in package["content"]
    assert "routes_v106" in " ".join(wired_route_modules())
    assert "governance_v106_ui.js" in Path("static/index.html").read_text(encoding="utf-8")
    assert Path("docs/V10_6_PROFILE_RESET_AUDIT_ROLLBACK.md").exists()
    out = tmp_path / "rollback.md"
    result = subprocess.run([sys.executable, "scripts/export_v10_6_rollback_snapshot.py", str(out)], text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "v10.6 Operator Rollback Snapshot Package" in out.read_text(encoding="utf-8")
