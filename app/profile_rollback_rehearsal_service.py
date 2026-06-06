from __future__ import annotations

import hashlib
import json
from datetime import date, datetime

from sqlalchemy.orm import Session

from app.profile_reset_orchestrator_service import approval_phrase
from app.profile_reset_snapshot_service import v10_6_rollback_snapshot_export
from app.sample_project_builder_data import SAMPLE_PROFILE_SEEDS

REQUIRED_TABLES = ["projects", "requirements", "work_items", "trace_links", "releases"]


def v10_7_manual_rollback_import_rehearsal(
    db: Session,
    profile_id: str = "core-risk",
    snapshot_export: dict | None = None,
) -> dict:
    source = snapshot_export or v10_6_rollback_snapshot_export(db, profile_id)
    snapshot = source.get("snapshot", source)
    validation = _validate_snapshot(profile_id, snapshot)
    data = {
        "version": "10.7",
        "mode": "manual-rollback-import-rehearsal",
        "status": "Rehearsal ready" if validation["ready"] else "Rehearsal blocked",
        "ready": validation["ready"],
        "profile_id": profile_id,
        "snapshot_digest": _digest(snapshot),
        "validation": validation,
        "dry_run_restore_steps": _restore_steps(profile_id, snapshot),
        "restore_checklist": _restore_checklist(profile_id),
        "safety_notes": _safety_notes(),
    }
    data["content"] = _rehearsal_markdown(data)
    return data


def v10_7_restore_checklist(profile_id: str = "core-risk") -> dict:
    known = profile_id in SAMPLE_PROFILE_SEEDS
    data = {
        "version": "10.7",
        "mode": "manual-restore-checklist",
        "status": "Ready" if known else "Unknown profile",
        "ready": known,
        "profile_id": profile_id,
        "approval_phrase": approval_phrase(profile_id) if known else "",
        "checklist": _restore_checklist(profile_id),
        "rollback_policy": _rollback_policy(),
    }
    data["content"] = _checklist_markdown(data)
    return data


def v10_7_operator_restore_package(db: Session, profile_id: str = "core-risk") -> dict:
    rehearsal = v10_7_manual_rollback_import_rehearsal(db, profile_id)
    checklist = v10_7_restore_checklist(profile_id)
    data = {
        "version": "10.7",
        "mode": "operator-manual-restore-package",
        "status": "Ready" if checklist["ready"] else checklist["status"],
        "ready": checklist["ready"],
        "profile_id": profile_id,
    }
    data["content"] = "# v10.7 Operator Manual Restore Package\n\n" + "\n\n".join(
        [rehearsal["content"], checklist["content"]]
    )
    return data


def _validate_snapshot(profile_id: str, snapshot: dict) -> dict:
    tables = snapshot.get("tables", {}) if isinstance(snapshot, dict) else {}
    checks = {
        "known_profile": profile_id in SAMPLE_PROFILE_SEEDS,
        "snapshot_ready": bool(snapshot.get("ready")) if isinstance(snapshot, dict) else False,
        "profile_matches": snapshot.get("profile_id") == profile_id if isinstance(snapshot, dict) else False,
        "has_project_row": bool(tables.get("projects")),
        "has_required_tables": all(name in tables for name in REQUIRED_TABLES[:3]),
    }
    warnings = []
    if not checks["snapshot_ready"]:
        warnings.append("Build the sample project and export a v10.6 snapshot first.")
    if not checks["profile_matches"]:
        warnings.append("Snapshot profile_id does not match the selected restore profile.")
    if "releases" not in tables:
        warnings.append("No release row found; dashboard restore may be incomplete.")
    return {"ready": all(checks.values()), "checks": checks, "warnings": warnings, "table_counts": _counts(tables)}


def _restore_steps(profile_id: str, snapshot: dict) -> list[str]:
    tables = snapshot.get("tables", {}) if isinstance(snapshot, dict) else {}
    names = ", ".join(sorted(tables)) or "no tables"
    return [
        f"Confirm profile `{profile_id}` and snapshot digest before touching data.",
        "Export the current database file as a separate safety copy.",
        "Run v10.5/v10.6 reset only with the exact approval phrase if rebuilding is needed.",
        f"Manually compare/import rows for these snapshot tables: {names}.",
        "Run dashboard, traceability, and tutorial progress smoke checks after import.",
    ]


def _restore_checklist(profile_id: str) -> list[str]:
    return [
        f"Use only a snapshot whose profile_id is `{profile_id}`.",
        "Verify snapshot digest against the exported operator package.",
        "Keep the pre-restore database copy until smoke tests pass.",
        "Restore project row before child rows that reference project_id.",
        "Restore requirements before work items and trace links.",
        "Do not restore into production without a separate production approval gate.",
    ]


def _rollback_policy() -> list[str]:
    return [
        "v10.7 rehearses manual import; it does not auto-write rollback rows.",
        "Automatic restore should be a later feature after repeated rehearsals pass.",
        "A wrong profile or digest mismatch must block operator restore.",
    ]


def _safety_notes() -> list[str]:
    return [
        "This is intentionally a dry-run restore rehearsal.",
        "The API validates shape and order, but does not mutate database rows.",
        "Rollback evidence should stay attached to the v10.6 audit event.",
    ]


def _counts(tables: dict) -> dict:
    return {name: len(rows) for name, rows in tables.items()}


def _json_default(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _digest(data: dict) -> str:
    payload = json.dumps(data, default=_json_default, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _rehearsal_markdown(data: dict) -> str:
    lines = ["# v10.7 Manual Rollback Import Rehearsal", "", f"Status: {data['status']}", f"Profile: {data['profile_id']}", f"Digest: `{data['snapshot_digest']}`", "", "## Validation"]
    checks = data["validation"]["checks"]
    lines.extend(f"- {name}: {value}" for name, value in checks.items())
    lines.extend(["", "## Dry-run restore steps"])
    lines.extend(f"{i}. {step}" for i, step in enumerate(data["dry_run_restore_steps"], 1))
    return "\n".join(lines).strip() + "\n"


def _checklist_markdown(data: dict) -> str:
    lines = ["# v10.7 Manual Restore Checklist", "", f"Profile: {data['profile_id']}", f"Approval phrase: `{data['approval_phrase']}`", "", "## Checklist"]
    lines.extend(f"- {item}" for item in data["checklist"])
    lines.extend(["", "## Policy", *[f"- {item}" for item in data["rollback_policy"]]])
    return "\n".join(lines).strip() + "\n"
