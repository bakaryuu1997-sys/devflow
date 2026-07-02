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


def test_v119_final_release_tag_preparation_is_ready():
    _prepare_profile()
    data = client.get("/api/release-governance/v11-9-final-release-tag-preparation?profile_id=core-risk").json()
    assert data["version"] == "11.9"
    assert data["ready"] is True
    assert data["release_tag"] == "devflow-guard-demo-v11.9"
    assert data["tag_signoff_phrase"] == "TAG RELEASE: devflow-guard-demo-v11.9"
    assert len(data["manifest_digest"]) == 64
    assert any("git tag -a" in command for command in data["git_commands"])


def test_v119_portfolio_demo_script_contains_story_sections():
    _prepare_profile()
    data = client.get("/api/release-governance/v11-9-portfolio-demo-script?profile_id=core-risk").json()
    assert data["version"] == "11.9"
    assert data["ready"] is True
    assert len(data["script_sections"]) >= 4
    assert any("digest" in item["say"].lower() for item in data["script_sections"])
    assert "pytest tests/test_v119_final_release_tag_portfolio.py" in data["verification_commands"]


def test_v119_operator_package_docs_ui_and_cli(tmp_path):
    _prepare_profile()
    package = client.get("/api/release-governance/v11-9-operator-final-release-package?profile_id=core-risk").json()
    assert package["version"] == "11.9"
    assert "v11.9 Operator Final Release Package" in package["content"]
    assert Path("docs/V11_9_FINAL_RELEASE_TAG_PORTFOLIO.md").exists()
    assert "routes_v119" in " ".join(wired_route_modules())
    assert "governance_v119_ui.js" in Path("static/governance_bundle.js").read_text(encoding="utf-8")
    out = tmp_path / "v11_9.md"
    result = subprocess.run(
        [sys.executable, "scripts/export_v11_9_final_release_package.py", str(out)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "Portfolio Demo Script" in out.read_text(encoding="utf-8")
