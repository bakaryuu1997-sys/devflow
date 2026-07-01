import sqlite3
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def test_v89_evidence_manifest_endpoints_are_wired():
    data = client.get("/api/release-governance/evidence-manifest").json()
    assert data["version"] == "8.9"
    assert data["mode"] == "evidence-manifest"
    assert data["algorithm"] == "sha256"
    assert len(data["manifest_hash"]) == 64
    assert "Evidence Manifest" in data["content"]


def test_v89_freeze_manifest_and_integrity_check_flow():
    frozen = client.post(
        "/api/release-governance/evidence-manifests", json={"notes": "Freeze current evidence."}
    ).json()
    assert frozen["status"] in {"Frozen", "Empty"}
    assert len(frozen["manifest_hash"]) == 64
    listed = client.get("/api/release-governance/evidence-manifests").json()
    assert listed["version"] == "8.9"
    assert listed["count"] >= 1
    integrity = client.get("/api/release-governance/export-bundle-integrity-check").json()
    assert integrity["version"] == "8.9"
    assert integrity["status"] in {"Verified", "Changed Since Freeze", "No Frozen Manifest"}
    assert "Export Bundle Integrity Check" in integrity["content"]


def test_v89_static_ui_and_routes_are_wired():
    index_html = Path("static/index.html").read_text(encoding="utf-8")
    routes_py = " ".join(wired_route_modules())
    ui_js = Path("static/evidence_manifest_ui.js").read_text(encoding="utf-8")
    assert "Evidence Manifest" in index_html
    assert "Bundle Integrity" in index_html
    assert "routes_v89" in routes_py
    assert "export-bundle-integrity-check" in ui_js


def test_v89_cli_manifest_and_integrity_exports(tmp_path):
    db_path = tmp_path / "v89.db"
    create_v89_database(db_path)
    manifest_out = tmp_path / "EVIDENCE_MANIFEST.md"
    integrity_out = tmp_path / "BUNDLE_INTEGRITY_CHECK.md"
    manifest = subprocess.run(
        [sys.executable, "scripts/export_evidence_manifest.py", str(db_path), str(manifest_out)],
        text=True,
        capture_output=True,
        check=False,
    )
    integrity = subprocess.run(
        [sys.executable, "scripts/verify_export_bundle_integrity.py", str(db_path), str(integrity_out)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert manifest.returncode == 0, manifest.stdout + manifest.stderr
    assert integrity.returncode == 0, integrity.stdout + integrity.stderr
    assert "evidence manifest" in manifest_out.read_text(encoding="utf-8").lower()
    assert "export bundle integrity" in integrity_out.read_text(encoding="utf-8").lower()


def create_v89_database(path: Path) -> None:
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
