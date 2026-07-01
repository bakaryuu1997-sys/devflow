import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def test_v96_verified_evidence_manifest_gate_endpoint():
    client.post(
        "/api/release-governance/public-verifier-evidence-attachments", json={"signer_name": "Fixture Operator"}
    )
    client.post("/api/release-governance/evidence-manifests", json={"notes": "freeze for v9.6"})
    data = client.get("/api/release-governance/verified-evidence-manifest-gate").json()
    assert data["version"] == "9.6"
    assert data["mode"] == "verified-evidence-manifest-gate"
    assert "Verified Evidence Manifest Gate" in data["content"]
    assert "hardening_rules" in data


def test_v97_verifier_profiles_and_policy_presets():
    created = client.post(
        "/api/release-governance/external-verifier-profiles",
        json={"name": "ops-ed25519", "key_reference": "ops-public-key"},
    ).json()
    assert created["name"] == "ops-ed25519"
    profiles = client.get("/api/release-governance/external-verifier-profiles").json()
    assert profiles["version"] == "9.7"
    assert profiles["count"] >= 1
    presets = client.get("/api/release-governance/operator-policy-presets").json()
    assert any(row["key"] == "standard-release" for row in presets["presets"])


def test_v98_final_signed_bundle_package_and_record():
    data = client.get("/api/release-governance/final-signed-evidence-bundle").json()
    assert data["version"] == "9.8"
    assert len(data["bundle_hash"]) == 64
    record = client.post("/api/release-governance/final-signed-evidence-bundles", json={}).json()
    assert record["status"] in {"Final", "Blocked"}
    listed = client.get("/api/release-governance/final-signed-evidence-bundles").json()
    assert listed["count"] >= 1


def test_v99_end_to_end_rehearsal_records():
    report = client.get("/api/release-governance/end-to-end-governance-rehearsal").json()
    assert report["version"] == "9.9"
    assert report["status"] in {"Go", "No-Go"}
    record = client.post("/api/release-governance/governance-rehearsal-records", json={}).json()
    assert record["status"] in {"Go", "No-Go"}


def test_v100_stable_milestone_and_installer_checklist():
    report = client.get("/api/release-governance/v10-stable-milestone-report").json()
    assert report["version"] == "10.0"
    assert "installer_steps" in report
    checklist = client.get("/api/release-governance/v10-installer-checklist").json()
    assert checklist["status"] == "Ready"
    assert "Installer Checklist" in checklist["content"]


def test_v96_to_v100_routes_ui_and_cli_exports(tmp_path):
    routes = " ".join(wired_route_modules())
    index = Path("static/index.html").read_text(encoding="utf-8")
    assert "routes_v100" in routes
    assert "Stable Milestone" in index
    bundle_out = tmp_path / "FINAL_SIGNED_EVIDENCE_BUNDLE.md"
    rehearsal_out = tmp_path / "GOVERNANCE_REHEARSAL.md"
    final_out = tmp_path / "V10_GOVERNANCE_PACKAGE.md"
    for cmd in [
        [sys.executable, "scripts/export_final_signed_evidence_bundle.py", str(bundle_out)],
        [sys.executable, "scripts/export_governance_rehearsal.py", str(rehearsal_out)],
        [sys.executable, "scripts/export_v10_governance_package.py", str(final_out)],
    ]:
        result = subprocess.run(cmd, text=True, capture_output=True, check=False)
        assert result.returncode == 0, result.stdout + result.stderr
    assert "Final Signed Release Evidence Bundle" in bundle_out.read_text(encoding="utf-8")
    assert "Governance Rehearsal" in rehearsal_out.read_text(encoding="utf-8")
    assert "Stable Milestone" in final_out.read_text(encoding="utf-8")
