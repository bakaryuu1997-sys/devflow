from pathlib import Path
import subprocess
import sys

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_v95_public_verifier_evidence_package_endpoint():
    data = client.get("/api/release-governance/public-verifier-evidence-package").json()
    assert data["version"] == "9.5"
    assert data["mode"] == "public-verifier-evidence-package"
    assert data["adapter"] == "ed25519-public-key"
    assert "never store private keys" in " ".join(data["rules"]).lower()
    assert "Public Verifier Evidence Package" in data["content"]


def test_v95_attach_verified_fixture_evidence_and_list_records():
    data = client.post("/api/release-governance/public-verifier-evidence-attachments", json={"signer_name": "Fixture Operator"}).json()
    assert data["verification_status"] == "Verified"
    assert data["gate_status"] == "Gate-Ready"
    assert len(data["payload_hash"]) == 64
    assert len(data["signature_hash"]) == 64
    listed = client.get("/api/release-governance/public-verifier-evidence-attachments").json()
    assert listed["version"] == "9.5"
    assert listed["count"] >= 1
    assert listed["records"][0]["verification_status"] == "Verified"


def test_v95_verified_signature_approval_gate_endpoint():
    client.post("/api/release-governance/public-verifier-evidence-attachments", json={"signer_name": "Fixture Operator"})
    data = client.get("/api/release-governance/verified-signature-approval-gate").json()
    assert data["version"] == "9.5"
    assert data["mode"] == "verified-signature-approval-gate"
    assert data["status"] in {"Gate Ready", "Blocked"}
    assert "Verified-Signature Approval Gate" in data["content"]
    assert data["latest_evidence"]["verification_status"] == "Verified"


def test_v95_static_ui_and_routes_are_wired():
    index_html = Path("static/index.html").read_text(encoding="utf-8")
    routes_py = Path("app/routes.py").read_text(encoding="utf-8")
    ui_js = Path("static/public_key_verifier_ui.js").read_text(encoding="utf-8")
    assert "Verifier Evidence" in index_html
    assert "Verified Gate" in index_html
    assert "routes_v95" in routes_py
    assert "public-verifier-evidence-attachments" in ui_js


def test_v95_cli_exports(tmp_path):
    package_out = tmp_path / "PUBLIC_VERIFIER_EVIDENCE_PACKAGE.md"
    gate_out = tmp_path / "VERIFIED_SIGNATURE_APPROVAL_GATE.md"
    package = subprocess.run([sys.executable, "scripts/export_public_verifier_evidence_package.py", str(package_out)], text=True, capture_output=True, check=False)
    gate = subprocess.run([sys.executable, "scripts/export_verified_signature_approval_gate.py", str(gate_out)], text=True, capture_output=True, check=False)
    assert package.returncode == 0, package.stdout + package.stderr
    assert gate.returncode == 0, gate.stdout + gate.stderr
    assert "Public Verifier Evidence Package" in package_out.read_text(encoding="utf-8")
    assert "Verified-Signature Approval Gate" in gate_out.read_text(encoding="utf-8")
