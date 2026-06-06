from pathlib import Path
import subprocess
import sys

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _prepare_profile():
    client.post("/api/demo/reset")
    client.post("/api/release-governance/v10-4-build-sample-project?profile_id=core-risk")


def test_v117_archive_integrity_manifest_is_ready_and_hashed():
    _prepare_profile()
    data = client.get("/api/release-governance/v11-7-archive-integrity-manifest?profile_id=core-risk").json()
    assert data["version"] == "11.7"
    assert data["ready"] is True
    assert data["release_candidate"] == "demo-rc-v11.5"
    assert len(data["manifest_digest"]) == 64
    assert all(item["exists"] for item in data["manifest"])
    assert any(item["path"] == "README.md" for item in data["manifest"])


def test_v117_release_notes_polish_has_operator_safe_scope():
    _prepare_profile()
    data = client.get("/api/release-governance/v11-7-release-notes-polish?profile_id=core-risk").json()
    assert data["version"] == "11.7"
    assert data["ready"] is True
    assert any("No new destructive" in item for item in data["highlights"])
    assert "Verification Notes" in data["content"]


def test_v117_operator_release_package_docs_ui_and_cli(tmp_path):
    _prepare_profile()
    package = client.get("/api/release-governance/v11-7-operator-release-package?profile_id=core-risk").json()
    assert package["version"] == "11.7"
    assert "v11.7 Operator Release Package" in package["content"]
    assert Path("docs/V11_7_ARCHIVE_INTEGRITY_RELEASE_NOTES.md").exists()
    assert "routes_v117" in Path("app/routes.py").read_text(encoding="utf-8")
    assert "governance_v117_ui.js" in Path("static/index.html").read_text(encoding="utf-8")
    out = tmp_path / "v11_7.md"
    result = subprocess.run([sys.executable, "scripts/export_v11_7_release_package.py", str(out)], text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    assert "Archive Integrity Manifest" in out.read_text(encoding="utf-8")
