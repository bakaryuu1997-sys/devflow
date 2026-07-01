import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def _snapshot_export():
    client.post("/api/demo/reset")
    client.post("/api/release-governance/v10-4-build-sample-project?profile_id=core-risk")
    fixture = client.get("/api/release-governance/v11-1-export-fixture-example?profile_id=core-risk").json()
    return fixture["fixture_payload"]["snapshot_export"]


def test_v113_recovery_smoke_test_runs_existing_safe_chain():
    _snapshot_export()
    data = client.get("/api/release-governance/v11-3-recovery-smoke-test-automation?profile_id=core-risk").json()
    assert data["version"] == "11.3"
    assert data["ready"] is True
    assert data["snapshot_digest_lock"]
    assert any(item["id"] == "fixture-validation-ready" and item["pass"] for item in data["checks"])
    assert any(item["id"] == "guarded-plan-ready" and item["pass"] for item in data["checks"])


def test_v113_post_restore_verification_compares_snapshot_and_current_rows():
    snapshot = _snapshot_export()
    data = client.post(
        "/api/release-governance/v11-3-post-restore-verification-report?profile_id=core-risk",
        json=snapshot,
    ).json()
    assert data["version"] == "11.3"
    assert data["ready"] is True
    assert data["expected_snapshot_digest"] == data["current_snapshot_digest"]
    assert any(item["id"] == "digest-match" and item["pass"] for item in data["checks"])
    assert any(item["id"] == "restore-audit-present" and item["severity"] == "warning" for item in data["checks"])


def test_v113_operator_package_docs_ui_and_cli(tmp_path):
    _snapshot_export()
    package = client.get(
        "/api/release-governance/v11-3-operator-smoke-verification-package?profile_id=core-risk"
    ).json()
    assert package["version"] == "11.3"
    assert "Operator Smoke Verification Package" in package["content"]
    assert Path("docs/V11_3_RECOVERY_SMOKE_VERIFICATION.md").exists()
    assert "routes_v113" in " ".join(wired_route_modules())
    assert "governance_v113_ui.js" in Path("static/index.html").read_text(encoding="utf-8")
    out = tmp_path / "smoke.md"
    result = subprocess.run(
        [sys.executable, "scripts/export_v11_3_operator_smoke_verification_package.py", str(out)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "v11.3 Operator Smoke Verification Package" in out.read_text(encoding="utf-8")
