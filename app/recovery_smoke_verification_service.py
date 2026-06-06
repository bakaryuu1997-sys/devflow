from __future__ import annotations

import hashlib
import json
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.profile_manual_restore_service import v10_8_restore_audit_trail
from app.profile_reset_snapshot_service import v10_6_rollback_snapshot_export
from app.profile_restore_conflict_service import v10_9_guarded_restore_plan, v10_9_restore_conflict_report, v10_9_restore_digest_lock_audit_trail
from app.recovery_fixture_validation_service import v11_2_fixture_validation_report
from app.recovery_ux_fixture_service import v11_1_export_fixture_example, v11_1_import_fixture_example
from app.sample_project_builder_service import v10_4_build_sample_project


def v11_3_recovery_smoke_test_automation(db: Session, profile_id: str = "core-risk") -> dict:
    build = v10_4_build_sample_project(db, profile_id, "v11.3-smoke-test")
    fixture = v11_1_export_fixture_example(db, profile_id)
    payload = fixture.get("fixture_payload", {})
    snapshot_export = payload.get("snapshot_export", {})
    validation = v11_2_fixture_validation_report(db, profile_id, payload)
    rehearsal = v11_1_import_fixture_example(db, profile_id, payload)
    conflict = v10_9_restore_conflict_report(db, profile_id, snapshot_export)
    plan = v10_9_guarded_restore_plan(db, profile_id, snapshot_export)
    checks = _smoke_checks(build, fixture, validation, rehearsal, conflict, plan)
    ready = all(item["pass"] for item in checks)
    data = {
        "version": "11.3",
        "mode": "recovery-smoke-test-automation",
        "status": "Recovery smoke test ready" if ready else "Recovery smoke test blocked",
        "ready": ready,
        "profile_id": profile_id,
        "snapshot_digest_lock": conflict.get("snapshot_digest_lock_required", ""),
        "checks": checks,
        "next_safe_action": "Run v10.9 guarded restore only with phrase and digest lock" if ready else "Fix failed smoke-test checks first",
    }
    data["content"] = _smoke_markdown(data)
    return data


def v11_3_post_restore_verification_report(db: Session, profile_id: str = "core-risk", snapshot_export: dict | None = None) -> dict:
    source = snapshot_export or v11_1_export_fixture_example(db, profile_id)["fixture_payload"]["snapshot_export"]
    expected_snapshot = source.get("snapshot", {}) if isinstance(source, dict) else {}
    current_export = v10_6_rollback_snapshot_export(db, profile_id)
    current_snapshot = current_export.get("snapshot", {})
    expected_digest = _digest(expected_snapshot)
    current_digest = _digest(current_snapshot)
    reset_counts = expected_snapshot.get("counts", {}) if isinstance(expected_snapshot, dict) else {}
    current_counts = current_snapshot.get("counts", {}) if isinstance(current_snapshot, dict) else {}
    restore_audit = v10_8_restore_audit_trail(db, profile_id)
    lock_audit = v10_9_restore_digest_lock_audit_trail(db, profile_id)
    checks = _post_restore_checks(expected_snapshot, current_snapshot, expected_digest, current_digest, reset_counts, current_counts, restore_audit, lock_audit)
    errors = [item for item in checks if item["severity"] == "error" and not item["pass"]]
    data = {
        "version": "11.3",
        "mode": "post-restore-verification-report",
        "status": "Post-restore verification passed" if not errors else "Post-restore verification blocked",
        "ready": not errors,
        "profile_id": profile_id,
        "expected_snapshot_digest": expected_digest,
        "current_snapshot_digest": current_digest,
        "checks": checks,
        "restore_audit_count": len(restore_audit.get("audit_events", [])),
        "digest_lock_audit_count": len(lock_audit.get("audit_events", [])),
    }
    data["content"] = _verify_markdown(data)
    return data


def v11_3_operator_smoke_verification_package(db: Session, profile_id: str = "core-risk") -> dict:
    smoke = v11_3_recovery_smoke_test_automation(db, profile_id)
    verification = v11_3_post_restore_verification_report(db, profile_id)
    data = {"version": "11.3", "mode": "operator-smoke-verification-package", "status": smoke["status"], "ready": smoke["ready"] and verification["ready"], "profile_id": profile_id}
    data["content"] = "# v11.3 Operator Smoke Verification Package\n\n" + "\n\n".join([smoke["content"], verification["content"]])
    return data


def _smoke_checks(build: dict, fixture: dict, validation: dict, rehearsal: dict, conflict: dict, plan: dict) -> list[dict]:
    return [
        _check("sample-project-built", build.get("ready"), "error", "v10.4 sample project exists before smoke test."),
        _check("fixture-export-ready", fixture.get("ready"), "error", "v11.1 fixture export is available."),
        _check("fixture-validation-ready", validation.get("ready"), "error", "v11.2 hardened validation passes."),
        _check("import-rehearsal-dry-run", rehearsal.get("ready") and rehearsal.get("dry_run", True), "error", "Import rehearsal stays non-mutating."),
        _check("digest-lock-present", bool(conflict.get("snapshot_digest_lock_required")), "error", "v10.9 digest lock can be copied."),
        _check("guarded-plan-ready", plan.get("ready"), "error", "v10.9 restore plan is ready but not executed."),
    ]


def _post_restore_checks(expected: dict, current: dict, expected_digest: str, current_digest: str, expected_counts: dict, current_counts: dict, restore_audit: dict, lock_audit: dict) -> list[dict]:
    restore_events = restore_audit.get("audit_events", [])
    lock_events = lock_audit.get("audit_events", [])
    return [
        _check("expected-snapshot-ready", expected.get("ready"), "error", "Expected rollback snapshot is ready."),
        _check("current-snapshot-ready", current.get("ready"), "error", "Current profile snapshot is readable."),
        _check("digest-match", expected_digest == current_digest, "error", "Current rows match expected snapshot digest."),
        _check("count-match", expected_counts == current_counts, "error", "Current table counts match expected snapshot counts."),
        _check("restore-audit-present", bool(restore_events), "warning", "At least one v10.8 restore audit event exists."),
        _check("digest-lock-audit-present", bool(lock_events), "warning", "At least one v10.9 digest-lock audit event exists."),
    ]


def _check(check_id: str, passed: bool, severity: str, detail: str) -> dict:
    return {"id": check_id, "pass": bool(passed), "severity": severity, "detail": detail}


def _json_default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _digest(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, default=_json_default, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def _smoke_markdown(data: dict) -> str:
    lines = ["# v11.3 Recovery Smoke-Test Automation", "", f"Status: {data['status']}", f"Profile: {data['profile_id']}", f"Digest lock: `{data['snapshot_digest_lock']}`", "", "## Checks"]
    lines.extend(f"- {'PASS' if item['pass'] else 'BLOCK'}: {item['id']} — {item['detail']}" for item in data["checks"])
    lines.append(f"\nNext safe action: {data['next_safe_action']}")
    return "\n".join(lines).strip() + "\n"


def _verify_markdown(data: dict) -> str:
    lines = ["# v11.3 Post-Restore Verification Report", "", f"Status: {data['status']}", f"Profile: {data['profile_id']}", f"Expected digest: `{data['expected_snapshot_digest']}`", f"Current digest: `{data['current_snapshot_digest']}`", "", "## Checks"]
    lines.extend(f"- {'PASS' if item['pass'] else item['severity'].upper()}: {item['id']} — {item['detail']}" for item in data["checks"])
    return "\n".join(lines).strip() + "\n"
