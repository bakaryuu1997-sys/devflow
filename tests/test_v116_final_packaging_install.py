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


def test_v116_final_packaging_cleanup_keeps_rc_and_non_destructive_scope():
    _prepare_profile()
    data = client.get("/api/release-governance/v11-6-final-packaging-cleanup?profile_id=core-risk").json()
    assert data["version"] == "11.6"
    assert data["ready"] is True
    assert data["release_candidate"] == "demo-rc-v11.5"
    assert all(item["pass"] for item in data["checks"] if item["required"])
    assert any("No destructive" in item for item in data["non_goals"])


def test_v116_beginner_install_verification_is_copyable():
    _prepare_profile()
    data = client.get("/api/release-governance/v11-6-beginner-install-verification?profile_id=core-risk").json()
    assert data["version"] == "11.6"
    assert data["ready"] is True
    assert "pip install -r requirements.txt" in data["verification_commands"]
    assert "pytest tests/test_v116_final_packaging_install.py" in data["verification_commands"]


def test_v116_operator_final_package_docs_ui_and_cli(tmp_path):
    _prepare_profile()
    package = client.get("/api/release-governance/v11-6-operator-final-package?profile_id=core-risk").json()
    assert package["version"] == "11.6"
    assert "v11.6 Operator Final Package" in package["content"]
    assert Path("docs/V11_6_FINAL_PACKAGING_INSTALL.md").exists()
    assert "routes_v116" in " ".join(wired_route_modules())
    assert "governance_v116_ui.js" in Path("static/governance_bundle.js").read_text(encoding="utf-8")
    out = tmp_path / "v11_6.md"
    result = subprocess.run(
        [sys.executable, "scripts/export_v11_6_operator_final_package.py", str(out)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Beginner Install Verification" in out.read_text(encoding="utf-8")
