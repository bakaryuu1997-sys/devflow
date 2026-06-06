from pathlib import Path
import subprocess
import sys

from fastapi.testclient import TestClient

from app.first_run_wizard_service import DEMO_RESET_APPROVAL
from app.main import app

client = TestClient(app)


def test_v102_first_run_wizard_reports_inventory_and_steps():
    client.post("/api/demo/reset")
    data = client.get("/api/release-governance/v10-2-first-run-wizard").json()
    assert data["version"] == "10.2"
    assert data["mode"] == "guided-first-run-wizard"
    assert data["workspace_inventory"]["projects"] >= 1
    assert len(data["steps"]) >= 6
    assert "Guided First-run Wizard" in data["content"]
    assert "private key" in data["content"].lower()


def test_v102_demo_reset_safety_check_and_plan_include_guardrails():
    client.post("/api/demo/reset")
    safety = client.get("/api/release-governance/v10-2-demo-reset-safety-check").json()
    assert safety["approval_phrase"] == DEMO_RESET_APPROVAL
    assert any("approval phrase" in item for item in safety["guardrails"])
    assert "Demo Reset Safety Check" in safety["content"]
    plan = client.get("/api/release-governance/v10-2-demo-reset-plan").json()
    assert DEMO_RESET_APPROVAL in plan["content"]
    assert "Hardened Demo Reset Plan" in plan["content"]


def test_v102_operator_package_routes_ui_and_cli_exports(tmp_path):
    package = client.get("/api/release-governance/v10-2-operator-first-run-package").json()
    assert package["ready"] is True
    assert "Operator First-run Package" in package["content"]
    routes = Path("app/routes.py").read_text(encoding="utf-8")
    index = Path("static/index.html").read_text(encoding="utf-8")
    assert "routes_v102" in routes
    assert "v10.2 First-run Wizard" in index
    assert "governance_v102_ui.js" in index
    outputs = [
        ("scripts/export_v10_2_first_run_wizard.py", "Guided First-run Wizard"),
        ("scripts/export_v10_2_demo_reset_safety.py", "Demo Reset Safety Check"),
        ("scripts/export_v10_2_operator_first_run_package.py", "Operator First-run Package"),
    ]
    for script, expected in outputs:
        out = tmp_path / (Path(script).stem + ".md")
        result = subprocess.run([sys.executable, script, str(out)], text=True, capture_output=True, check=False)
        assert result.returncode == 0, result.stdout + result.stderr
        assert expected in out.read_text(encoding="utf-8")
