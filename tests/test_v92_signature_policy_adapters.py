import sqlite3
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def test_v92_signature_adapter_and_policy_endpoints():
    adapters = client.get("/api/release-governance/signature-verification-adapter-stubs").json()
    assert adapters["version"] == "9.2"
    assert adapters["mode"] == "signature-verification-adapter-stubs"
    assert "generic-sha256-reference" in [row["name"] for row in adapters["adapters"]]
    policy = client.get("/api/release-governance/policy-based-verification-checklist").json()
    assert policy["version"] == "9.2"
    assert policy["mode"] == "policy-based-verification-checklist"
    assert len(policy["checklist"]) >= 5


def test_v92_signature_adapter_dry_run_endpoint():
    policy = client.get("/api/release-governance/policy-based-verification-checklist").json()
    result = client.post(
        "/api/release-governance/signature-adapter-dry-run",
        json={
            "adapter": "generic-sha256-reference",
            "payload_hash": policy["payload_hash"],
            "signature_hash": "a" * 64,
            "token_hash": "b" * 64,
        },
    ).json()
    assert result["version"] == "9.2"
    assert result["mode"] == "signature-adapter-dry-run"
    assert result["adapter"] == "generic-sha256-reference"
    assert "Signature Adapter Dry Run" in result["content"]


def test_v92_static_ui_and_routes_are_wired():
    index_html = Path("static/index.html").read_text(encoding="utf-8")
    routes_py = " ".join(wired_route_modules())
    ui_js = Path("static/signature_policy_ui.js").read_text(encoding="utf-8")
    assert "Signature Adapters" in index_html
    assert "Verification Policy" in index_html
    assert "routes_v92" in routes_py
    assert "signature-verification-adapter-stubs" in ui_js


def test_v92_cli_policy_and_dry_run(tmp_path):
    db_path = tmp_path / "v92.db"
    create_minimal_evidence_db(db_path)
    policy_out = tmp_path / "SIGNATURE_POLICY_CHECKLIST.md"
    dry_out = tmp_path / "SIGNATURE_ADAPTER_DRY_RUN.md"
    policy = subprocess.run(
        [sys.executable, "scripts/export_signature_policy_checklist.py", str(db_path), str(policy_out)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert policy.returncode == 0, policy.stdout + policy.stderr
    payload_hash = extract_payload_hash(policy_out.read_text(encoding="utf-8"))
    dry = subprocess.run(
        [
            sys.executable,
            "scripts/signature_adapter_dry_run.py",
            str(db_path),
            "generic-sha256-reference",
            payload_hash,
            "a" * 64,
            str(dry_out),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert dry.returncode in {0, 1}, dry.stdout + dry.stderr
    assert "Policy-Based Verification Checklist" in policy_out.read_text(encoding="utf-8")
    assert "Signature Adapter Dry Run" in dry_out.read_text(encoding="utf-8")


def create_minimal_evidence_db(path: Path) -> None:
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


def extract_payload_hash(markdown: str) -> str:
    marker = "Payload hash: `"
    start = markdown.index(marker) + len(marker)
    return markdown[start : start + 64]
