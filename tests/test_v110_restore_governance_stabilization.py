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


def test_v110_stability_report_requires_digest_lock_and_gates():
    snapshot = _snapshot()
    report = client.post(
        "/api/release-governance/v11-0-restore-governance-stability-report?profile_id=core-risk",
        json=snapshot,
    ).json()
    assert report["version"] == "11.0"
    assert report["snapshot_digest_lock_required"] == snapshot["snapshot_digest"]
    assert report["restore_approval_phrase"] == "RESTORE DEMO PROFILE: core-risk"
    assert any(gate["id"] == "digest-lock-present" and gate["ready"] for gate in report["stability_gates"])


def test_v110_final_runbook_preserves_v109_restore_guardrails():
    snapshot = _snapshot()
    runbook = client.post(
        "/api/release-governance/v11-0-final-operator-recovery-runbook?profile_id=core-risk",
        json=snapshot,
    ).json()
    assert runbook["version"] == "11.0"
    assert "snapshot digest lock" in "\n".join(runbook["required_inputs"])
    assert "v10.9 restore" in "\n".join(runbook["recovery_sequence"])
    assert "v11.0 Final Operator Recovery Runbook" in runbook["content"]


def test_v110_routes_ui_docs_and_cli_export(tmp_path):
    package = client.get("/api/release-governance/v11-0-operator-recovery-package?profile_id=core-risk").json()
    assert package["version"] == "11.0"
    assert "Final Operator Recovery Package" in package["content"]
    assert "routes_v110" in " ".join(wired_route_modules())
    assert "governance_v110_ui.js" in Path("static/governance_bundle.js").read_text(encoding="utf-8")
    assert Path("docs/V11_0_RESTORE_GOVERNANCE_STABILIZATION.md").exists()
    out = tmp_path / "recovery.md"
    result = subprocess.run(
        [sys.executable, "scripts/export_v11_0_operator_recovery_package.py", str(out)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "v11.0 Final Operator Recovery Package" in out.read_text(encoding="utf-8")
