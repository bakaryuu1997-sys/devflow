from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.profile_manual_restore_service import restore_approval_phrase
from app.profile_reset_orchestrator_service import approval_phrase as reset_phrase
from app.profile_reset_snapshot_service import v10_6_rollback_snapshot_export
from app.profile_restore_conflict_service import v10_9_restore_conflict_report
from app.profile_rollback_rehearsal_service import v10_7_manual_rollback_import_rehearsal
from app.restore_governance_stabilization_service import v11_0_final_operator_recovery_runbook


def v11_1_recovery_ux_summary(db: Session, profile_id: str = "core-risk") -> dict:
    snapshot = v10_6_rollback_snapshot_export(db, profile_id)
    conflict = v10_9_restore_conflict_report(db, profile_id, snapshot)
    data = {
        "version": "11.1",
        "mode": "recovery-ux-polish-summary",
        "status": "Recovery UX guide ready" if snapshot["ready"] else snapshot["status"],
        "ready": snapshot["ready"],
        "profile_id": profile_id,
        "operator_cards": _operator_cards(profile_id, snapshot, conflict),
        "copy_targets": _copy_targets(profile_id, snapshot, conflict),
        "safety_labels": _safety_labels(),
    }
    data["content"] = _summary_markdown(data)
    return data


def v11_1_export_fixture_example(db: Session, profile_id: str = "core-risk") -> dict:
    snapshot = v10_6_rollback_snapshot_export(db, profile_id)
    fixture = _fixture_payload(profile_id, snapshot)
    data = {
        "version": "11.1",
        "mode": "rollback-export-fixture-example",
        "status": "Fixture example ready" if snapshot["ready"] else snapshot["status"],
        "ready": snapshot["ready"],
        "profile_id": profile_id,
        "fixture_payload": fixture,
        "fixture_json": json.dumps(fixture, indent=2, sort_keys=True),
        "usage_notes": _fixture_usage_notes(),
    }
    data["content"] = _fixture_markdown(data)
    return data


def v11_1_import_fixture_example(
    db: Session, profile_id: str = "core-risk", fixture_payload: dict | None = None
) -> dict:
    payload = fixture_payload or v11_1_export_fixture_example(db, profile_id)["fixture_payload"]
    snapshot_export = payload.get("snapshot_export", payload)
    rehearsal = v10_7_manual_rollback_import_rehearsal(db, profile_id, snapshot_export)
    data = {
        "version": "11.1",
        "mode": "rollback-import-fixture-example",
        "status": "Import fixture rehearsal ready" if rehearsal["ready"] else "Import fixture blocked",
        "ready": rehearsal["ready"],
        "profile_id": profile_id,
        "fixture_name": payload.get("fixture_name", "inline-snapshot-export"),
        "snapshot_digest": rehearsal["snapshot_digest"],
        "rehearsal": rehearsal,
        "import_steps": _import_steps(profile_id),
    }
    data["content"] = _import_markdown(data)
    return data


def v11_1_operator_fixture_package(db: Session, profile_id: str = "core-risk") -> dict:
    summary = v11_1_recovery_ux_summary(db, profile_id)
    export_fixture = v11_1_export_fixture_example(db, profile_id)
    import_fixture = v11_1_import_fixture_example(db, profile_id, export_fixture["fixture_payload"])
    runbook = v11_0_final_operator_recovery_runbook(db, profile_id)
    data = {
        "version": "11.1",
        "mode": "operator-recovery-fixture-package",
        "status": import_fixture["status"],
        "ready": all([summary["ready"], export_fixture["ready"], import_fixture["ready"]]),
        "profile_id": profile_id,
    }
    data["content"] = "# v11.1 Operator Recovery Fixture Package\n\n" + "\n\n".join(
        [summary["content"], export_fixture["content"], import_fixture["content"], runbook["content"]]
    )
    return data


def _operator_cards(profile_id: str, snapshot: dict, conflict: dict) -> list[dict]:
    return [
        {
            "title": "1. Export snapshot",
            "state": snapshot["status"],
            "copy": "GET /api/release-governance/v10-6-rollback-snapshot",
        },
        {
            "title": "2. Rehearse import",
            "state": "Dry-run only",
            "copy": "POST /api/release-governance/v11-1-import-fixture-example",
        },
        {"title": "3. Lock digest", "state": conflict["status"], "copy": conflict["snapshot_digest_lock_required"]},
        {"title": "4. Restore manually", "state": "Guarded execution", "copy": restore_approval_phrase(profile_id)},
    ]


def _copy_targets(profile_id: str, snapshot: dict, conflict: dict) -> dict:
    return {
        "reset_phrase": reset_phrase(profile_id),
        "restore_phrase": restore_approval_phrase(profile_id),
        "snapshot_digest_lock": conflict["snapshot_digest_lock_required"],
        "snapshot_digest": snapshot["snapshot_digest"],
    }


def _fixture_payload(profile_id: str, snapshot: dict) -> dict:
    return {
        "fixture_name": f"{profile_id}-rollback-snapshot-example",
        "fixture_version": "11.1",
        "purpose": "manual rollback import rehearsal example",
        "profile_id": profile_id,
        "snapshot_export": snapshot,
    }


def _safety_labels() -> list[str]:
    return [
        "Dry-run import fixture is safe and non-destructive.",
        "Restore execution still needs restore phrase plus snapshot digest lock.",
        "Fixture examples are operator aids, not automatic restore jobs.",
    ]


def _fixture_usage_notes() -> list[str]:
    return [
        "Save fixture_json as an example payload for the import rehearsal endpoint.",
        "Do not edit profile_id or snapshot_digest by hand.",
        "Run rehearsal before copying the digest lock into a restore request.",
    ]


def _import_steps(profile_id: str) -> list[str]:
    return [
        "Paste the fixture JSON into the v11.1 import fixture endpoint.",
        f"Confirm the returned profile is {profile_id}.",
        "Confirm rehearsal.ready is true before restore.",
        "Copy snapshot_digest only from the validated response.",
    ]


def _summary_markdown(data: dict) -> str:
    lines = [
        "# v11.1 Recovery UX Summary",
        "",
        f"Status: {data['status']}",
        f"Profile: {data['profile_id']}",
        "",
        "## Operator Cards",
    ]
    for card in data["operator_cards"]:
        lines.append(f"- {card['title']}: {card['state']} — `{card['copy']}`")
    lines.extend(["", "## Safety Labels", *[f"- {item}" for item in data["safety_labels"]]])
    return "\n".join(lines).strip() + "\n"


def _fixture_markdown(data: dict) -> str:
    lines = [
        "# v11.1 Export Fixture Example",
        "",
        f"Status: {data['status']}",
        f"Profile: {data['profile_id']}",
        "",
        "## Usage Notes",
    ]
    lines.extend(f"- {item}" for item in data["usage_notes"])
    lines.extend(["", "## Fixture JSON", "```json", data["fixture_json"], "```"])
    return "\n".join(lines).strip() + "\n"


def _import_markdown(data: dict) -> str:
    lines = [
        "# v11.1 Import Fixture Example",
        "",
        f"Status: {data['status']}",
        f"Fixture: {data['fixture_name']}",
        f"Snapshot digest: `{data['snapshot_digest']}`",
        "",
        "## Import Steps",
    ]
    lines.extend(f"{index}. {item}" for index, item in enumerate(data["import_steps"], start=1))
    return "\n".join(lines).strip() + "\n"
