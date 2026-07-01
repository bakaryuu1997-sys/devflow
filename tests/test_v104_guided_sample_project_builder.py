import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.demo_profiles_data import TUTORIAL_STEPS
from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def test_v104_sample_builder_preview_and_build_are_safe():
    client.post("/api/demo/reset")
    preview = client.get("/api/release-governance/v10-4-sample-project-builder?profile_id=core-risk").json()
    assert preview["version"] == "10.4"
    assert preview["ready"] is True
    assert preview["sample_preview"]["requirements"] == 1
    built = client.post(
        "/api/release-governance/v10-4-build-sample-project?profile_id=core-risk&operator_name=Long"
    ).json()
    assert built["status"] == "Built"
    assert built["project_id"] > 0
    assert built["created_or_reused"]["requirements"] == 1
    projects = client.get("/api/projects").json()
    assert any(row["name"] == "Payroll Guided Sample" for row in projects)


def test_v104_completion_badge_tracks_all_tutorial_steps():
    client.post("/api/demo/reset")
    badge = client.get("/api/release-governance/v10-4-tutorial-completion-badge").json()
    assert badge["badge"]["earned"] is False
    for step_id, _, _ in TUTORIAL_STEPS:
        client.post(f"/api/release-governance/v10-3-tutorial-progress/{step_id}?status=Done")
    earned = client.get("/api/release-governance/v10-4-tutorial-completion-badge").json()
    assert earned["badge"]["earned"] is True
    assert earned["badge"]["label"] == "Tutorial Complete"
    assert "Tutorial Completion Badge" in earned["content"]


def test_v104_routes_ui_docs_and_cli_export(tmp_path):
    package = client.get("/api/release-governance/v10-4-operator-sample-builder-package").json()
    assert package["ready"] is True
    assert "Operator Sample Builder Package" in package["content"]
    assert "routes_v104" in " ".join(wired_route_modules())
    assert "governance_v104_ui.js" in Path("static/index.html").read_text(encoding="utf-8")
    assert Path("docs/V10_4_GUIDED_SAMPLE_PROJECT_BUILDER.md").exists()
    out = tmp_path / "builder.md"
    result = subprocess.run(
        [sys.executable, "scripts/export_v10_4_operator_sample_builder_package.py", str(out)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "v10.4 Operator Sample Builder Package" in out.read_text(encoding="utf-8")
