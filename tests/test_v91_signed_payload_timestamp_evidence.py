import sqlite3
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def test_v91_signed_payload_import_and_timestamp_token_endpoints():
    package = client.get("/api/release-governance/signed-payload-import-package").json()
    assert package["version"] == "9.1"
    assert package["mode"] == "signed-payload-import-package"
    assert len(package["payload_hash"]) == 64
    created = client.post("/api/release-governance/signed-payload-verifications", json={"payload_hash": package["payload_hash"], "signature_hash": "b" * 64, "signer_name": "Test Operator", "signature_reference": "SIG-1"}).json()
    assert created["verification_status"] in {"Verified", "Blocked"}
    listed = client.get("/api/release-governance/signed-payload-verifications").json()
    assert listed["count"] >= 1


def test_v91_timestamp_token_attachment_and_integrity_endpoint():
    handoff_package = client.get("/api/release-governance/external-timestamp-handoff-package").json()
    client.post("/api/release-governance/external-timestamp-handoffs", json={"timestamp_authority": "Test TSA", "request_reference": "REQ-91", "response_token_hash": "c" * 64})
    token_package = client.get("/api/release-governance/timestamp-token-evidence-package").json()
    assert token_package["version"] == "9.1"
    attached = client.post("/api/release-governance/timestamp-token-evidence-attachments", json={"payload_hash": token_package["payload_hash"], "token_hash": "d" * 64, "timestamp_authority": "Test TSA", "token_reference": "TOK-1"}).json()
    assert attached["verification_status"] in {"Verified", "Blocked", "Payload Hash Mismatch"}
    integrity = client.get("/api/release-governance/signed-payload-timestamp-integrity-check").json()
    assert integrity["version"] == "9.1"
    assert integrity["mode"] == "signed-payload-timestamp-integrity-check"
    assert "Signed Payload + Timestamp" in integrity["content"]
    assert len(handoff_package["payload_hash"]) == 64


def test_v91_static_ui_and_routes_are_wired():
    index_html = Path("static/index.html").read_text(encoding="utf-8")
    routes_py = " ".join(wired_route_modules())
    ui_js = Path("static/signature_import_ui.js").read_text(encoding="utf-8")
    assert "Signed Payload Import" in index_html
    assert "Timestamp Token Evidence" in index_html
    assert "routes_v91" in routes_py
    assert "signed-payload-import-package" in ui_js


def test_v91_cli_exports_and_verification(tmp_path):
    db_path = tmp_path / "v91.db"
    create_v91_database(db_path)
    signed_out = tmp_path / "SIGNED_PAYLOAD_IMPORT_PACKAGE.md"
    token_out = tmp_path / "TIMESTAMP_TOKEN_EVIDENCE_PACKAGE.md"
    signed = subprocess.run([sys.executable, "scripts/export_signed_payload_import_package.py", str(db_path), str(signed_out)], text=True, capture_output=True, check=False)
    token = subprocess.run([sys.executable, "scripts/export_timestamp_token_evidence_package.py", str(db_path), str(token_out)], text=True, capture_output=True, check=False)
    assert signed.returncode == 0, signed.stdout + signed.stderr
    assert token.returncode == 0, token.stdout + token.stderr
    assert "signed payload import" in signed_out.read_text(encoding="utf-8").lower()
    assert "timestamp token evidence" in token_out.read_text(encoding="utf-8").lower()


def create_v91_database(path: Path) -> None:
    con = sqlite3.connect(path)
    try:
        con.execute("CREATE TABLE signed_rehearsal_artifacts (id INTEGER PRIMARY KEY, status TEXT DEFAULT '', content TEXT DEFAULT '', created_at TEXT DEFAULT '')")
        con.execute("CREATE TABLE operator_approval_records (id INTEGER PRIMARY KEY, signed_artifact_id INTEGER, status TEXT DEFAULT '', content TEXT DEFAULT '', created_at TEXT DEFAULT '')")
        con.execute("CREATE TABLE evidence_manifest_records (id INTEGER PRIMARY KEY, algorithm TEXT DEFAULT 'sha256', manifest_hash TEXT DEFAULT '', bundle_hash TEXT DEFAULT '', status TEXT DEFAULT '', artifact_count INTEGER DEFAULT 0, approval_count INTEGER DEFAULT 0, item_count INTEGER DEFAULT 0, notes TEXT DEFAULT '', content TEXT DEFAULT '', created_at TEXT DEFAULT '')")
        con.execute("CREATE TABLE external_timestamp_handoff_records (id INTEGER PRIMARY KEY, payload_hash TEXT DEFAULT '', manifest_hash TEXT DEFAULT '', bundle_hash TEXT DEFAULT '', timestamp_authority TEXT DEFAULT '', request_reference TEXT DEFAULT '', response_token_hash TEXT DEFAULT '', status TEXT DEFAULT '', notes TEXT DEFAULT '', content TEXT DEFAULT '', created_at TEXT DEFAULT '')")
        con.execute("INSERT INTO signed_rehearsal_artifacts (status, content, created_at) VALUES ('Signed', 'artifact content', '2026-06-04T00:00:00')")
        con.commit()
    finally:
        con.close()
