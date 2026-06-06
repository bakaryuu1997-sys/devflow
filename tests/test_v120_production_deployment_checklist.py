from pathlib import Path
import subprocess
import sys

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _prepare_profile():
    client.post("/api/demo/reset")
    client.post("/api/release-governance/v10-4-build-sample-project?profile_id=core-risk")


def test_v120_baseline_freeze_keeps_v119_as_demo_baseline():
    _prepare_profile()
    data = client.get("/api/release-governance/v12-0-baseline-freeze-summary?profile_id=core-risk").json()
    assert data["version"] == "12.0"
    assert data["ready"] is True
    assert data["baseline_version"] == "11.9"
    assert data["release_tag"] == "devflow-guard-demo-v11.9"
    assert "No new feature endpoint." in data["non_goals"]


def test_v120_deployment_checklist_makes_vercel_static_decision_clear():
    _prepare_profile()
    data = client.get("/api/release-governance/v12-0-production-deployment-checklist?profile_id=core-risk").json()
    assert data["version"] == "12.0"
    assert data["ready"] is True
    assert "deploy docs/static first" in data["decision"]
    assert any(item["name"] == "Vercel static/docs" for item in data["hosting_options"])
    assert any("uvicorn app.main:app" in cmd for cmd in data["local_verification"])


def test_v120_operator_package_docs_ui_and_cli(tmp_path):
    _prepare_profile()
    package = client.get("/api/release-governance/v12-0-operator-deployment-package?profile_id=core-risk").json()
    assert package["version"] == "12.0"
    assert "v12.0 Operator Deployment Package" in package["content"]
    assert Path("docs/V12_0_PRODUCTION_DEPLOYMENT_CHECKLIST.md").exists()
    assert "routes_v120" in Path("app/routes.py").read_text(encoding="utf-8")
    assert "governance_v120_ui.js" in Path("static/index.html").read_text(encoding="utf-8")
    out = tmp_path / "v12_0.md"
    result = subprocess.run([sys.executable, "scripts/export_v12_0_deployment_package.py", str(out)], text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    assert "Production Deployment Checklist" in out.read_text(encoding="utf-8")
