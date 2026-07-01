import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def test_v103_demo_profiles_and_reset_plan_are_available():
    data = client.get("/api/release-governance/v10-3-demo-data-profiles").json()
    assert data["version"] == "10.3"
    assert data["mode"] == "demo-data-profiles"
    assert len(data["profiles"]) >= 3
    assert "Core Risk Demo" in data["content"]
    plan = client.get("/api/release-governance/v10-3-demo-profile-reset-plan?profile_id=core-risk").json()
    assert plan["ready"] is True
    assert "Demo Profile Reset Plan" in plan["content"]


def test_v103_tutorial_progress_can_mark_step_done():
    client.post("/api/demo/reset")
    before = client.get("/api/release-governance/v10-3-tutorial-progress").json()
    assert before["completion_percent"] >= 0
    saved = client.post("/api/release-governance/v10-3-tutorial-progress/profile?status=Done&operator_name=Long").json()
    assert saved["status"] == "Saved"
    after = client.get("/api/release-governance/v10-3-tutorial-progress").json()
    profile = [row for row in after["steps"] if row["step_id"] == "profile"][0]
    assert profile["status"] == "Done"
    assert "Tutorial Mode Progress" in after["content"]


def test_v103_package_routes_ui_and_cli_exports(tmp_path):
    package = client.get("/api/release-governance/v10-3-operator-tutorial-package").json()
    assert package["ready"] is True
    assert "Operator Tutorial Package" in package["content"]
    routes = " ".join(wired_route_modules())
    index = Path("static/index.html").read_text(encoding="utf-8")
    assert "routes_v103" in routes
    assert "v10.3 Demo Profiles" in index
    assert "governance_v103_ui.js" in index
    outputs = [
        ("scripts/export_v10_3_demo_profiles.py", "Demo Data Profiles"),
        ("scripts/export_v10_3_tutorial_progress.py", "Tutorial Mode Progress"),
        ("scripts/export_v10_3_operator_tutorial_package.py", "Operator Tutorial Package"),
    ]
    for script, expected in outputs:
        out = tmp_path / (Path(script).stem + ".md")
        result = subprocess.run([sys.executable, script, str(out)], text=True, capture_output=True, check=False)
        assert result.returncode == 0, result.stdout + result.stderr
        assert expected in out.read_text(encoding="utf-8")
