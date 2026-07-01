import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def _prepare_profile():
    client.post("/api/demo/reset")
    client.post("/api/release-governance/v10-4-build-sample-project?profile_id=core-risk")


def test_v115_demo_release_candidate_freeze_uses_existing_evidence():
    _prepare_profile()
    data = client.get("/api/release-governance/v11-5-demo-release-candidate-freeze?profile_id=core-risk").json()
    assert data["version"] == "11.5"
    assert data["ready"] is True
    assert data["freeze_state"] == "frozen"
    assert data["immutable_copy_targets"]["snapshot_digest_lock"]
    assert all(gate["pass"] for gate in data["freeze_gates"] if gate["required"])


def test_v115_operator_acceptance_checklist_is_copyable_and_non_destructive():
    _prepare_profile()
    data = client.get("/api/release-governance/v11-5-operator-acceptance-checklist?profile_id=core-risk").json()
    assert data["version"] == "11.5"
    assert data["ready"] is True
    assert data["signoff_phrase"] == "ACCEPT DEMO RC: demo-rc-v11.5"
    assert all(item["checked"] for item in data["checklist"] if item["required"])


def test_v115_operator_package_docs_ui_and_cli(tmp_path):
    _prepare_profile()
    package = client.get("/api/release-governance/v11-5-operator-release-candidate-package?profile_id=core-risk").json()
    assert package["version"] == "11.5"
    assert "v11.5 Operator Release Candidate Package" in package["content"]
    assert Path("docs/V11_5_DEMO_RELEASE_CANDIDATE_FREEZE.md").exists()
    assert "routes_v115" in " ".join(wired_route_modules())
    assert "governance_v115_ui.js" in Path("static/index.html").read_text(encoding="utf-8")
    out = tmp_path / "v11_5.md"
    result = subprocess.run([sys.executable, "scripts/export_v11_5_operator_release_candidate_package.py", str(out)], text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    assert "ACCEPT DEMO RC: demo-rc-v11.5" in out.read_text(encoding="utf-8")
