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


def test_v118_signed_archive_checksum_handoff_is_ready():
    _prepare_profile()
    data = client.get("/api/release-governance/v11-8-signed-archive-checksum-handoff?profile_id=core-risk").json()
    assert data["version"] == "11.8"
    assert data["ready"] is True
    assert data["release_candidate"] == "demo-rc-v11.5"
    assert len(data["manifest_digest"]) == 64
    assert len(data["handoff_signature"]) == 64
    assert data["signoff_label"] == "SIGNED CHECKSUM HANDOFF: demo-rc-v11.5"


def test_v118_final_quickstart_contains_beginner_commands():
    _prepare_profile()
    data = client.get("/api/release-governance/v11-8-final-user-facing-quickstart?profile_id=core-risk").json()
    assert data["version"] == "11.8"
    assert data["ready"] is True
    assert any("pip install -r requirements.txt" in step for step in data["steps"])
    assert "python -m compileall app scripts" in data["verification_commands"]


def test_v118_operator_package_docs_ui_and_cli(tmp_path):
    _prepare_profile()
    package = client.get("/api/release-governance/v11-8-operator-checksum-quickstart-package?profile_id=core-risk").json()
    assert package["version"] == "11.8"
    assert "v11.8 Operator Checksum Quickstart Package" in package["content"]
    assert Path("docs/V11_8_SIGNED_CHECKSUM_QUICKSTART.md").exists()
    assert "routes_v118" in " ".join(wired_route_modules())
    assert "governance_v118_ui.js" in Path("static/index.html").read_text(encoding="utf-8")
    out = tmp_path / "v11_8.md"
    result = subprocess.run([sys.executable, "scripts/export_v11_8_checksum_quickstart_package.py", str(out)], text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    assert "Signed Archive Checksum Handoff" in out.read_text(encoding="utf-8")
