from pathlib import Path
import subprocess
import sys

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_v105_reset_plan_exposes_profile_specific_approval_phrase():
    client.post("/api/demo/reset")
    plan = client.get("/api/release-governance/v10-5-profile-reset-plan?profile_id=core-risk").json()
    assert plan["version"] == "10.5"
    assert plan["ready"] is True
    assert plan["approval_phrase"] == "RESET DEMO PROFILE: core-risk"
    assert "Payroll Guided Sample" in plan["target_project"]
    assert "not a full database drop" in " ".join(plan["guardrails"])


def test_v105_blocks_reset_without_exact_approval_phrase():
    client.post("/api/demo/reset")
    blocked = client.post("/api/release-governance/v10-5-execute-profile-reset?profile_id=core-risk&approval=wrong").json()
    assert blocked["ready"] is False
    assert blocked["status"] == "Approval phrase required"
    assert blocked["expected_approval_phrase"] == "RESET DEMO PROFILE: core-risk"


def test_v105_executes_scoped_profile_reset_and_rebuilds_seed_data():
    client.post("/api/demo/reset")
    phrase = "RESET DEMO PROFILE: core-risk"
    first = client.post("/api/release-governance/v10-4-build-sample-project?profile_id=core-risk").json()
    assert first["status"] == "Built"
    reset = client.post(f"/api/release-governance/v10-5-execute-profile-reset?profile_id=core-risk&approval={phrase}&operator_name=Long").json()
    assert reset["status"] == "Reset complete"
    assert reset["deleted_records"]["projects"] == 1
    projects = client.get("/api/projects").json()
    names = [row["name"] for row in projects]
    assert names.count("Payroll Guided Sample") == 1
    assert "Payroll System" in names


def test_v105_routes_ui_docs_and_cli_export(tmp_path):
    package = client.get("/api/release-governance/v10-5-operator-reset-package?profile_id=core-risk").json()
    assert package["ready"] is True
    assert "Operator Profile Reset Package" in package["content"]
    assert "routes_v105" in Path("app/routes.py").read_text(encoding="utf-8")
    assert "governance_v105_ui.js" in Path("static/index.html").read_text(encoding="utf-8")
    assert Path("docs/V10_5_PROFILE_SPECIFIC_DEMO_RESET.md").exists()
    out = tmp_path / "reset.md"
    result = subprocess.run([sys.executable, "scripts/export_v10_5_operator_reset_package.py", str(out)], text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "v10.5 Operator Profile Reset Package" in out.read_text(encoding="utf-8")
