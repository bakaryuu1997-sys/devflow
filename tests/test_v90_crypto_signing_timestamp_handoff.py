import sqlite3
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def test_v90_crypto_signing_readiness_endpoints_are_wired():
    data = client.get("/api/release-governance/cryptographic-signing-readiness").json()
    assert data["version"] == "9.0"
    assert data["mode"] == "cryptographic-signing-readiness"
    assert data["algorithm"] == "sha256"
    assert len(data["payload_hash"]) == 64
    assert "Cryptographic Signing Readiness" in data["content"]


def test_v90_timestamp_handoff_flow_and_integrity():
    package = client.get("/api/release-governance/external-timestamp-handoff-package").json()
    assert package["version"] == "9.0"
    assert package["mode"] == "external-timestamp-handoff-package"
    assert len(package["payload_hash"]) == 64
    created = client.post(
        "/api/release-governance/external-timestamp-handoffs",
        json={"timestamp_authority": "Test TSA", "request_reference": "REQ-1", "response_token_hash": "a" * 64},
    ).json()
    assert created["status"] == "Timestamped"
    assert created["timestamp_authority"] == "Test TSA"
    listed = client.get("/api/release-governance/external-timestamp-handoffs").json()
    assert listed["count"] >= 1
    integrity = client.get("/api/release-governance/timestamp-handoff-integrity-check").json()
    assert integrity["version"] == "9.0"
    assert integrity["status"] in {"Verified", "No Matching Handoff"}


def test_v90_static_ui_and_routes_are_wired():
    index_html = Path("static/index.html").read_text(encoding="utf-8")
    routes_py = " ".join(wired_route_modules())
    ui_js = Path("static/crypto_signing_ui.js").read_text(encoding="utf-8")
    assert "Signing Readiness" in index_html
    assert "Timestamp Handoff" in index_html
    assert "routes_v90" in routes_py
    assert "cryptographic-signing-readiness" in ui_js


def test_v90_cli_exports(tmp_path):
    db_path = tmp_path / "v90.db"
    create_v90_database(db_path)
    signing_out = tmp_path / "SIGNING_READINESS.md"
    handoff_out = tmp_path / "TIMESTAMP_HANDOFF_PACKAGE.md"
    signing = subprocess.run(
        [sys.executable, "scripts/export_signing_readiness.py", str(db_path), str(signing_out)],
        text=True,
        capture_output=True,
        check=False,
    )
    handoff = subprocess.run(
        [sys.executable, "scripts/export_timestamp_handoff_package.py", str(db_path), str(handoff_out)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert signing.returncode == 0, signing.stdout + signing.stderr
    assert handoff.returncode == 0, handoff.stdout + handoff.stderr
    assert "cryptographic signing readiness" in signing_out.read_text(encoding="utf-8").lower()
    assert "external timestamp handoff" in handoff_out.read_text(encoding="utf-8").lower()


def create_v90_database(path: Path) -> None:
    con = sqlite3.connect(path)
    try:
        con.execute(
            "CREATE TABLE signed_rehearsal_artifacts (id INTEGER PRIMARY KEY, status TEXT DEFAULT '', content TEXT DEFAULT '', created_at TEXT DEFAULT '')"
        )
        con.execute(
            "CREATE TABLE operator_approval_records (id INTEGER PRIMARY KEY, signed_artifact_id INTEGER, status TEXT DEFAULT '', content TEXT DEFAULT '', created_at TEXT DEFAULT '')"
        )
        con.execute(
            "CREATE TABLE evidence_manifest_records (id INTEGER PRIMARY KEY, algorithm TEXT DEFAULT 'sha256', manifest_hash TEXT DEFAULT '', bundle_hash TEXT DEFAULT '', status TEXT DEFAULT '', artifact_count INTEGER DEFAULT 0, approval_count INTEGER DEFAULT 0, item_count INTEGER DEFAULT 0, notes TEXT DEFAULT '', content TEXT DEFAULT '', created_at TEXT DEFAULT '')"
        )
        con.execute(
            "INSERT INTO signed_rehearsal_artifacts (status, content, created_at) VALUES ('Signed', 'artifact content', '2026-06-04T00:00:00')"
        )
        con.commit()
    finally:
        con.close()
