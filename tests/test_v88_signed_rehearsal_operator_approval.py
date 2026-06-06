from pathlib import Path
import sqlite3
import subprocess
import sys

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_v88_signed_rehearsal_package_endpoint_is_wired():
    data = client.get("/api/release-governance/signed-rehearsal-artifact-package").json()
    assert data["version"] == "8.8"
    assert data["mode"] == "signed-rehearsal-artifact-package"
    assert "required_signature_text" in data
    assert "Signed Rehearsal Artifact Package" in data["content"]


def test_v88_signed_artifact_and_final_approval_flow():
    signature = "I ran and reviewed the production upgrade rehearsal on a copied database."
    artifact = client.post("/api/release-governance/signed-rehearsal-artifacts", json={
        "operator_name": "Operator A",
        "reviewer_name": "Reviewer A",
        "signature_text": signature,
        "notes": "Rehearsal passed on DB copy.",
    }).json()
    assert artifact["status"] in {"Signed", "Blocked"}
    blocked = client.post("/api/release-governance/final-operator-approval-records", json={
        "approver_name": "Approver A",
        "approval_phrase": "WRONG",
        "approval_note": "Wrong phrase should block.",
    }).json()
    assert blocked["status"] == "Blocked"
    if artifact["status"] == "Signed":
        approved = client.post("/api/release-governance/final-operator-approval-records", json={
            "approver_name": "Approver A",
            "approval_phrase": "I_APPROVE_PRODUCTION_MIGRATION",
            "approval_note": "Approved after signed rehearsal.",
        }).json()
        assert approved["status"] == "Approved"
        assert approved["signed_artifact_id"] == artifact["id"]


def test_v88_list_endpoints_and_static_ui_are_wired():
    artifacts = client.get("/api/release-governance/signed-rehearsal-artifacts").json()
    approvals = client.get("/api/release-governance/final-operator-approval-records").json()
    index_html = Path("static/index.html").read_text(encoding="utf-8")
    routes_py = Path("app/routes.py").read_text(encoding="utf-8")
    ui_js = Path("static/migration_operator_approval_ui.js").read_text(encoding="utf-8")
    assert artifacts["version"] == "8.8"
    assert approvals["version"] == "8.8"
    assert "Signed Artifact Package" in index_html
    assert "Final Operator Approval" in index_html
    assert "routes_v88" in routes_py
    assert "signed-rehearsal-artifact-package" in ui_js


def test_v88_cli_exports_for_signed_package_and_final_approval(tmp_path):
    db_path = tmp_path / "v88.db"
    create_v88_database(db_path)
    package_out = tmp_path / "SIGNED_REHEARSAL_PACKAGE.md"
    approval_out = tmp_path / "FINAL_OPERATOR_APPROVAL_RECORD.md"
    package = subprocess.run([sys.executable, "scripts/export_signed_rehearsal_package.py", str(db_path), str(package_out)], text=True, capture_output=True, check=False)
    approval = subprocess.run([sys.executable, "scripts/final_operator_approval_record.py", str(db_path), str(approval_out)], text=True, capture_output=True, check=False)
    assert package.returncode == 0, package.stdout + package.stderr
    assert approval.returncode == 0, approval.stdout + approval.stderr
    assert "signed rehearsal artifact package" in package_out.read_text(encoding="utf-8").lower()
    assert "final operator approval record" in approval_out.read_text(encoding="utf-8").lower()


def create_v88_database(path: Path) -> None:
    con = sqlite3.connect(path)
    try:
        con.execute("CREATE TABLE signed_rehearsal_artifacts (id INTEGER PRIMARY KEY, status TEXT DEFAULT '')")
        con.execute("CREATE TABLE operator_approval_records (id INTEGER PRIMARY KEY, status TEXT DEFAULT '')")
        con.commit()
    finally:
        con.close()
