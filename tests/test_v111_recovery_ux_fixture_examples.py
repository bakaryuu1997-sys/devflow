import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def _fixture():
    client.post("/api/demo/reset")
    client.post("/api/release-governance/v10-4-build-sample-project?profile_id=core-risk")
    return client.get("/api/release-governance/v11-1-export-fixture-example?profile_id=core-risk").json()


def test_v111_recovery_ux_summary_exposes_copy_targets():
    client.post("/api/demo/reset")
    client.post("/api/release-governance/v10-4-build-sample-project?profile_id=core-risk")
    data = client.get("/api/release-governance/v11-1-recovery-ux-summary?profile_id=core-risk").json()
    assert data["version"] == "11.1"
    assert data["copy_targets"]["restore_phrase"] == "RESTORE DEMO PROFILE: core-risk"
    assert data["copy_targets"]["reset_phrase"] == "RESET DEMO PROFILE: core-risk"
    assert any(card["title"].startswith("2. Rehearse") for card in data["operator_cards"])


def test_v111_export_and_import_fixture_examples_are_dry_run_ready():
    exported = _fixture()
    assert exported["version"] == "11.1"
    assert exported["fixture_payload"]["snapshot_export"]["version"] == "10.6"
    imported = client.post(
        "/api/release-governance/v11-1-import-fixture-example?profile_id=core-risk",
        json=exported["fixture_payload"],
    ).json()
    assert imported["version"] == "11.1"
    assert imported["ready"] is True
    assert imported["rehearsal"]["mode"] == "manual-rollback-import-rehearsal"
    assert "v11.1 Import Fixture Example" in imported["content"]


def test_v111_routes_ui_docs_and_cli_export(tmp_path):
    package = client.get("/api/release-governance/v11-1-operator-fixture-package?profile_id=core-risk").json()
    assert package["version"] == "11.1"
    assert "Operator Recovery Fixture Package" in package["content"]
    assert "routes_v111" in " ".join(wired_route_modules())
    assert "governance_v111_ui.js" in Path("static/governance_bundle.js").read_text(encoding="utf-8")
    assert Path("docs/V11_1_RECOVERY_UX_FIXTURE_EXAMPLES.md").exists()
    out = tmp_path / "fixtures.md"
    result = subprocess.run(
        [sys.executable, "scripts/export_v11_1_operator_fixture_package.py", str(out)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "v11.1 Operator Recovery Fixture Package" in out.read_text(encoding="utf-8")
