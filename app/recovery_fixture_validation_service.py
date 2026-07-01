from __future__ import annotations

import hashlib
import json
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.profile_manual_restore_service import restore_approval_phrase
from app.profile_reset_orchestrator_service import approval_phrase as reset_phrase
from app.profile_restore_conflict_service import v10_9_restore_conflict_report
from app.profile_rollback_rehearsal_service import REQUIRED_TABLES, v10_7_manual_rollback_import_rehearsal
from app.recovery_ux_fixture_service import v11_1_export_fixture_example, v11_1_operator_fixture_package
from app.sample_project_builder_data import SAMPLE_PROFILE_SEEDS


def v11_2_fixture_validation_report(db: Session, profile_id: str = "core-risk", fixture_payload: dict | None = None) -> dict:
    payload = fixture_payload or v11_1_export_fixture_example(db, profile_id)["fixture_payload"]
    snapshot_export = payload.get("snapshot_export", {}) if isinstance(payload, dict) else {}
    snapshot = snapshot_export.get("snapshot", {}) if isinstance(snapshot_export, dict) else {}
    checks = _validation_checks(profile_id, payload, snapshot_export, snapshot)
    errors = [item for item in checks if item["severity"] == "error" and not item["pass"]]
    warnings = [item for item in checks if item["severity"] == "warning" and not item["pass"]]
    rehearsal = v10_7_manual_rollback_import_rehearsal(db, profile_id, snapshot_export)
    conflict = v10_9_restore_conflict_report(db, profile_id, snapshot_export)
    ready = not errors and rehearsal["ready"]
    data = {
        "version": "11.2",
        "mode": "recovery-fixture-validation-hardening",
        "status": "Fixture validation hardened and ready" if ready else "Fixture validation blocked",
        "ready": ready,
        "profile_id": profile_id,
        "fixture_name": payload.get("fixture_name", "inline-fixture") if isinstance(payload, dict) else "invalid-fixture",
        "snapshot_digest": snapshot_export.get("snapshot_digest", "") if isinstance(snapshot_export, dict) else "",
        "computed_snapshot_digest": _digest(snapshot),
        "checks": checks,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "rehearsal_ready": rehearsal["ready"],
        "conflict_count": len(conflict["conflicts"]),
        "safe_to_restore": ready and bool(conflict["snapshot_digest_lock_required"]),
    }
    data["content"] = _validation_markdown(data)
    return data


def v11_2_sample_operator_walkthrough(db: Session, profile_id: str = "core-risk") -> dict:
    fixture = v11_1_export_fixture_example(db, profile_id)["fixture_payload"]
    report = v11_2_fixture_validation_report(db, profile_id, fixture)
    data = {
        "version": "11.2",
        "mode": "sample-operator-recovery-walkthrough",
        "status": "Walkthrough ready" if report["ready"] else "Walkthrough generated with blockers",
        "ready": report["ready"],
        "profile_id": profile_id,
        "copy_targets": _copy_targets(profile_id, report),
        "walkthrough_steps": _walkthrough_steps(profile_id),
        "sample_requests": _sample_requests(profile_id, report),
        "validation_report": report,
    }
    data["content"] = _walkthrough_markdown(data)
    return data


def v11_2_operator_walkthrough_package(db: Session, profile_id: str = "core-risk") -> dict:
    base = v11_1_operator_fixture_package(db, profile_id)
    validation = v11_2_fixture_validation_report(db, profile_id)
    walkthrough = v11_2_sample_operator_walkthrough(db, profile_id)
    data = {
        "version": "11.2",
        "mode": "operator-fixture-validation-walkthrough-package",
        "status": walkthrough["status"],
        "ready": validation["ready"] and walkthrough["ready"],
        "profile_id": profile_id,
    }
    data["content"] = "# v11.2 Operator Fixture Validation Walkthrough Package\n\n" + "\n\n".join(
        [validation["content"], walkthrough["content"], base["content"]]
    )
    return data


def _validation_checks(profile_id: str, payload: dict, snapshot_export: dict, snapshot: dict) -> list[dict]:
    tables = snapshot.get("tables", {}) if isinstance(snapshot, dict) else {}
    payload_profile = payload.get("profile_id") if isinstance(payload, dict) else None
    exported_profile = snapshot_export.get("profile_id") if isinstance(snapshot_export, dict) else None
    exported_digest = snapshot_export.get("snapshot_digest") if isinstance(snapshot_export, dict) else None
    computed_digest = _digest(snapshot)
    required = ["projects", "requirements", "work_items"]
    return [
        _check("known-profile", profile_id in SAMPLE_PROFILE_SEEDS, "error", "Selected profile must exist in demo catalog."),
        _check("fixture-version", payload.get("fixture_version") == "11.1" if isinstance(payload, dict) else False, "warning", "Fixture should come from v11.1 export."),
        _check("snapshot-export-version", snapshot_export.get("version") == "10.6" if isinstance(snapshot_export, dict) else False, "error", "Snapshot export must be v10.6."),
        _check("payload-profile-match", payload_profile == profile_id, "error", "Fixture profile_id must match selected profile."),
        _check("snapshot-profile-match", exported_profile == profile_id and snapshot.get("profile_id") == profile_id, "error", "Snapshot profile must match selected profile."),
        _check("snapshot-ready", bool(snapshot.get("ready")), "error", "Snapshot must be ready before import rehearsal."),
        _check("digest-lock-match", exported_digest == computed_digest, "error", "Exported digest must match snapshot payload digest."),
        _check("has-project-row", bool(tables.get("projects")), "error", "Snapshot must include a project row."),
        _check("required-tables", all(name in tables for name in required), "error", "Snapshot must include project, requirement, and work item tables."),
        _check("full-restore-table-set", all(name in tables for name in REQUIRED_TABLES), "warning", "Release and trace tables are recommended for complete walkthroughs."),
    ]


def _check(check_id: str, passed: bool, severity: str, detail: str) -> dict:
    return {"id": check_id, "pass": bool(passed), "severity": severity, "detail": detail}


def _copy_targets(profile_id: str, report: dict) -> dict:
    return {
        "reset_phrase": reset_phrase(profile_id),
        "restore_phrase": restore_approval_phrase(profile_id),
        "snapshot_digest_lock": report["computed_snapshot_digest"],
        "validation_endpoint": "/api/release-governance/v11-2-fixture-validation-report",
    }


def _walkthrough_steps(profile_id: str) -> list[str]:
    return [
        "Build or reuse the v10.4 guided sample project.",
        "Export the v11.1 fixture example and save the JSON payload.",
        "Run the v11.2 validation report against the exact payload.",
        "Run the v11.1 import rehearsal and confirm it stays dry-run only.",
        f"Copy only the validated digest lock for `{profile_id}` into restore planning.",
        "Execute restore only through v10.9 when restore phrase and digest lock both match.",
    ]


def _sample_requests(profile_id: str, report: dict) -> list[dict]:
    return [
        {"label": "export fixture", "method": "GET", "path": f"/api/release-governance/v11-1-export-fixture-example?profile_id={profile_id}"},
        {"label": "validate fixture", "method": "POST", "path": f"/api/release-governance/v11-2-fixture-validation-report?profile_id={profile_id}"},
        {"label": "restore guard input", "restore_approval": restore_approval_phrase(profile_id), "snapshot_digest_lock": report["computed_snapshot_digest"]},
    ]


def _json_default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _digest(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, default=_json_default, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def _validation_markdown(data: dict) -> str:
    lines = ["# v11.2 Recovery Fixture Validation Report", "", f"Status: {data['status']}", f"Profile: {data['profile_id']}", f"Computed digest: `{data['computed_snapshot_digest']}`", "", "## Checks"]
    for item in data["checks"]:
        mark = "PASS" if item["pass"] else item["severity"].upper()
        lines.append(f"- {mark}: {item['id']} — {item['detail']}")
    return "\n".join(lines).strip() + "\n"


def _walkthrough_markdown(data: dict) -> str:
    lines = ["# v11.2 Sample Operator Walkthrough", "", f"Status: {data['status']}", f"Profile: {data['profile_id']}", "", "## Steps"]
    lines.extend(f"{i}. {step}" for i, step in enumerate(data["walkthrough_steps"], 1))
    lines.extend(["", "## Copy Targets"])
    lines.extend(f"- {key}: `{value}`" for key, value in data["copy_targets"].items())
    return "\n".join(lines).strip() + "\n"
