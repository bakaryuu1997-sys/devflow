import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def test_v101_usability_walkthrough_and_demo_script():
    walkthrough = client.get("/api/release-governance/v10-1-usability-walkthrough").json()
    assert walkthrough["version"] == "10.1"
    assert walkthrough["status"] == "Ready"
    assert len(walkthrough["steps"]) >= 5
    assert "Usability Walkthrough" in walkthrough["content"]
    demo = client.get("/api/release-governance/v10-1-sample-demo-script").json()
    assert demo["mode"] == "sample-demo-script"
    assert any(row["title"] == "Governance" for row in demo["script_sections"])


def test_v101_deployment_guide_and_quickstart_package():
    guide = client.get("/api/release-governance/v10-1-optional-deployment-guide").json()
    assert guide["version"] == "10.1"
    assert any(row["mode"] == "local-dev" for row in guide["deployment_modes"])
    assert "No private-key storage" in guide["content"]
    package = client.get("/api/release-governance/v10-1-operator-quickstart-package").json()
    assert package["ready"] is True
    assert "Sample Demo Script" in package["content"]
    assert "Optional Local Deployment Guide" in package["content"]


def test_v101_routes_ui_and_cli_exports(tmp_path):
    routes = " ".join(wired_route_modules())
    index = Path("static/index.html").read_text(encoding="utf-8")
    assert "routes_v101" in routes
    assert "v10.1 Demo Script" in index
    outputs = [
        ("scripts/export_v10_1_demo_script.py", "Sample Demo Script"),
        ("scripts/export_v10_1_deployment_guide.py", "Optional Local Deployment Guide"),
        ("scripts/export_v10_1_operator_quickstart.py", "Operator Quickstart"),
    ]
    for script, expected in outputs:
        out = tmp_path / (Path(script).stem + ".md")
        result = subprocess.run([sys.executable, script, str(out)], text=True, capture_output=True, check=False)
        assert result.returncode == 0, result.stdout + result.stderr
        assert expected in out.read_text(encoding="utf-8")
