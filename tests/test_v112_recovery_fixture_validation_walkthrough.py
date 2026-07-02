import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def _fixture():
    client.post("/api/demo/reset")
    client.post("/api/release-governance/v10-4-build-sample-project?profile_id=core-risk")
    return client.get("/api/release-governance/v11-1-export-fixture-example?profile_id=core-risk").json()[
        "fixture_payload"
    ]


def test_v112_fixture_validation_accepts_valid_fixture():
    data = client.post(
        "/api/release-governance/v11-2-fixture-validation-report?profile_id=core-risk",
        json=_fixture(),
    ).json()
    assert data["version"] == "11.2"
    assert data["ready"] is True
    assert data["error_count"] == 0
    assert data["safe_to_restore"] is True
    assert data["computed_snapshot_digest"] == data["snapshot_digest"]


def test_v112_fixture_validation_blocks_profile_mismatch():
    payload = _fixture()
    payload["profile_id"] = "clean-release"
    data = client.post(
        "/api/release-governance/v11-2-fixture-validation-report?profile_id=core-risk",
        json=payload,
    ).json()
    assert data["ready"] is False
    assert data["error_count"] >= 1
    assert any(item["id"] == "payload-profile-match" and not item["pass"] for item in data["checks"])


def test_v112_walkthrough_exposes_copy_targets_and_routes():
    client.post("/api/demo/reset")
    client.post("/api/release-governance/v10-4-build-sample-project?profile_id=core-risk")
    data = client.get("/api/release-governance/v11-2-sample-operator-walkthrough?profile_id=core-risk").json()
    assert data["version"] == "11.2"
    assert data["copy_targets"]["restore_phrase"] == "RESTORE DEMO PROFILE: core-risk"
    assert any("v11.2 validation" in step for step in data["walkthrough_steps"])
    assert "routes_v112" in " ".join(wired_route_modules())
    assert "governance_v112_ui.js" in Path("static/governance_bundle.js").read_text(encoding="utf-8")


def test_v112_docs_and_cli_export(tmp_path):
    package = client.get("/api/release-governance/v11-2-operator-walkthrough-package?profile_id=core-risk").json()
    assert package["version"] == "11.2"
    assert "Operator Fixture Validation Walkthrough Package" in package["content"]
    assert Path("docs/V11_2_RECOVERY_FIXTURE_VALIDATION_WALKTHROUGH.md").exists()
    out = tmp_path / "walkthrough.md"
    result = subprocess.run(
        [sys.executable, "scripts/export_v11_2_operator_walkthrough_package.py", str(out)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "v11.2 Operator Fixture Validation Walkthrough Package" in out.read_text(encoding="utf-8")
