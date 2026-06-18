from pathlib import Path

from app.main import app


def test_workspace_routes_are_registered():
    paths = {getattr(route, "path", "") for route in app.routes}

    assert "/workspace" in paths
    assert "/workspace/" in paths


def test_workspace_route_serves_operator_workspace_source():
    html = Path("static/workspace.html").read_text(encoding="utf-8")

    assert "Workspace History" in html
    assert "Browser-local state" in html
    assert "exportWorkspaceHistory" in html
