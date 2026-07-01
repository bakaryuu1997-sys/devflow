import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.routes import wired_route_modules

client = TestClient(app)


def _prepare_profile_snapshot():
    client.post("/api/demo/reset")
    client.post("/api/release-governance/v10-4-build-sample-project?profile_id=core-risk")
    return client.get("/api/release-governance/v10-6-rollback-snapshot?profile_id=core-risk").json()


def test_v107_rehearses_current_v106_snapshot_without_writing_restore_rows():
    snapshot = _prepare_profile_snapshot()
    result = client.get("/api/release-governance/v10-7-manual-rollback-import-rehearsal?profile_id=core-risk").json()
    assert result["version"] == "10.7"
    assert result["ready"] is True
    assert result["validation"]["checks"]["profile_matches"] is True
    assert result["validation"]["table_counts"]["projects"] == 1
    assert result["snapshot_digest"] == snapshot["snapshot_digest"]
    assert "Manual Rollback Import Rehearsal" in result["content"]


def test_v107_accepts_snapshot_payload_and_blocks_mismatched_profile():
    snapshot = _prepare_profile_snapshot()
    result = client.post(
        "/api/release-governance/v10-7-manual-rollback-import-rehearsal?profile_id=clean-release",
        json=snapshot,
    ).json()
    assert result["version"] == "10.7"
    assert result["ready"] is False
    assert result["validation"]["checks"]["profile_matches"] is False
    assert result["validation"]["warnings"]


def test_v107_restore_checklist_routes_ui_docs_and_cli_export(tmp_path):
    package = client.get("/api/release-governance/v10-7-operator-restore-package?profile_id=core-risk").json()
    checklist = client.get("/api/release-governance/v10-7-restore-checklist?profile_id=core-risk").json()
    assert package["ready"] is True
    assert checklist["approval_phrase"] == "RESET DEMO PROFILE: core-risk"
    assert "Operator Manual Restore Package" in package["content"]
    assert "routes_v107" in " ".join(wired_route_modules())
    assert "governance_v107_ui.js" in Path("static/index.html").read_text(encoding="utf-8")
    assert Path("docs/V10_7_MANUAL_ROLLBACK_IMPORT_REHEARSAL.md").exists()
    out = tmp_path / "restore.md"
    result = subprocess.run(
        [sys.executable, "scripts/export_v10_7_restore_rehearsal.py", str(out)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "v10.7 Operator Manual Restore Package" in out.read_text(encoding="utf-8")
