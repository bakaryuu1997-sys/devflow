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


def test_v114_recovery_evidence_bundle_collects_required_proof():
    _prepare_profile()
    data = client.get("/api/release-governance/v11-4-recovery-evidence-bundle?profile_id=core-risk").json()
    assert data["version"] == "11.4"
    assert data["ready"] is True
    assert data["snapshot_digest"]
    assert data["snapshot_digest_lock"]
    assert data["handoff_gate"] == "demo-ready"
    assert all(item["ready"] for item in data["evidence_sections"] if item["required"])


def test_v114_final_demo_handoff_keeps_restore_non_destructive():
    _prepare_profile()
    data = client.get("/api/release-governance/v11-4-final-demo-handoff-polish?profile_id=core-risk").json()
    assert data["version"] == "11.4"
    assert data["ready"] is True
    assert "No new destructive endpoint." in data["non_goals"]
    assert data["copy_targets"]["restore_phrase"].startswith("RESTORE DEMO PROFILE:")
    assert any(card["title"].startswith("3. Prove lock") for card in data["demo_cards"])


def test_v114_operator_package_docs_ui_and_cli(tmp_path):
    _prepare_profile()
    package = client.get("/api/release-governance/v11-4-operator-demo-handoff-package?profile_id=core-risk").json()
    assert package["version"] == "11.4"
    assert "v11.4 Operator Demo Handoff Package" in package["content"]
    assert Path("docs/V11_4_RECOVERY_EVIDENCE_HANDOFF.md").exists()
    assert "routes_v114" in " ".join(wired_route_modules())
    assert "governance_v114_ui.js" in Path("static/index.html").read_text(encoding="utf-8")
    out = tmp_path / "v11_4.md"
    result = subprocess.run([sys.executable, "scripts/export_v11_4_operator_demo_handoff_package.py", str(out)], text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    assert "v11.4 Operator Demo Handoff Package" in out.read_text(encoding="utf-8")
