from pathlib import Path
import subprocess
import sys

from fastapi.testclient import TestClient

from app.main import app
from app.public_key_verifier_fixtures import fixture_metadata, load_fixture_evidence
from app.public_key_verifier_service import public_key_verifier_dry_run

client = TestClient(app)


def test_v94_public_key_verifier_readiness_endpoint():
    data = client.get("/api/release-governance/public-key-verifier-readiness").json()
    assert data["version"] == "9.4"
    assert data["mode"] == "public-key-verifier-readiness"
    assert data["adapter"] == "ed25519-public-key"
    assert data["private_key_storage"] == "not-supported"
    assert "cryptography" == data["optional_dependency"]
    assert "Public-Key Verifier Readiness" in data["content"]


def test_v94_fixture_package_has_no_private_key_material():
    data = client.get("/api/release-governance/public-key-verifier-fixture-package").json()
    assert data["version"] == "9.4"
    assert data["mode"] == "public-key-verifier-fixture-package"
    assert data["fixture"]["all_files_present"] is True
    assert data["fixture"]["contains_private_key_marker"] is False
    assert not data["blockers"]
    assert len(data["fixture"]["files"]) == 3


def test_v94_real_public_key_fixture_dry_run_verifies():
    data = client.post("/api/release-governance/public-key-verifier-dry-run", json={"use_fixture": True}).json()
    assert data["version"] == "9.4"
    assert data["mode"] == "public-key-verifier-dry-run"
    assert data["adapter"] == "ed25519-public-key"
    assert data["status"] == "Verified"
    assert data["verified"] is True
    assert not data["findings"]
    assert len(data["payload_hash"]) == 64


def test_v94_rejects_tampered_payload():
    evidence = load_fixture_evidence()
    payload = {
        "use_fixture": False,
        "payload_text": "tampered payload",
        "public_key_pem": evidence["public_key_pem"],
        "signature_b64": Path("fixtures/signature_adapters/ed25519_public_key_sample/signature.b64").read_text().strip(),
    }
    with client:
        data = client.post("/api/release-governance/public-key-verifier-dry-run", json=payload).json()
    assert data["verified"] is False
    assert data["status"] == "Invalid Signature"
    assert "Ed25519 signature verification failed." in data["findings"]


def test_v94_fixture_metadata_and_static_ui_are_wired():
    meta = fixture_metadata()
    index_html = Path("static/index.html").read_text(encoding="utf-8")
    routes_py = Path("app/routes.py").read_text(encoding="utf-8")
    assert meta["all_files_present"] is True
    assert meta["contains_private_key_marker"] is False
    assert "Public-key Verifier" in index_html
    assert "public_key_verifier_ui.js" in index_html
    assert "routes_v94" in routes_py


def test_v94_cli_exports(tmp_path):
    readiness_out = tmp_path / "PUBLIC_KEY_VERIFIER_READINESS.md"
    dry_run_out = tmp_path / "PUBLIC_KEY_VERIFIER_DRY_RUN.md"
    readiness = subprocess.run([sys.executable, "scripts/export_public_key_verifier_readiness.py", str(readiness_out)], text=True, capture_output=True, check=False)
    dry_run = subprocess.run([sys.executable, "scripts/public_key_verifier_dry_run.py", str(dry_run_out)], text=True, capture_output=True, check=False)
    assert readiness.returncode == 0, readiness.stdout + readiness.stderr
    assert dry_run.returncode == 0, dry_run.stdout + dry_run.stderr
    assert "Public-Key Verifier Readiness" in readiness_out.read_text(encoding="utf-8")
    assert "Public-Key Verifier Dry Run" in dry_run_out.read_text(encoding="utf-8")
