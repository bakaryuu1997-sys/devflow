from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.profile_reset_snapshot_service import v10_6_rollback_snapshot_export
from app.profile_restore_conflict_service import v10_9_restore_conflict_report
from app.recovery_fixture_validation_service import v11_2_sample_operator_walkthrough
from app.recovery_smoke_verification_service import (
    v11_3_operator_smoke_verification_package,
    v11_3_post_restore_verification_report,
    v11_3_recovery_smoke_test_automation,
)
from app.recovery_ux_fixture_service import v11_1_export_fixture_example


def v11_4_recovery_evidence_bundle(db: Session, profile_id: str = "core-risk") -> dict:
    snapshot = v10_6_rollback_snapshot_export(db, profile_id)
    fixture = v11_1_export_fixture_example(db, profile_id)
    smoke = v11_3_recovery_smoke_test_automation(db, profile_id)
    verify = v11_3_post_restore_verification_report(db, profile_id)
    conflict = v10_9_restore_conflict_report(db, profile_id, snapshot)
    sections = _evidence_sections(snapshot, fixture, smoke, verify, conflict)
    ready = all(item["ready"] for item in sections if item["required"])
    data = {
        "version": "11.4",
        "mode": "recovery-evidence-bundle",
        "status": "Recovery evidence bundle ready" if ready else "Recovery evidence bundle blocked",
        "ready": ready,
        "profile_id": profile_id,
        "generated_on": date.today().isoformat(),
        "snapshot_digest": snapshot.get("snapshot_digest", ""),
        "snapshot_digest_lock": conflict.get("snapshot_digest_lock_required", ""),
        "evidence_sections": sections,
        "handoff_gate": "demo-ready" if ready else "fix-required-evidence",
    }
    data["content"] = _bundle_markdown(data)
    return data


def v11_4_final_demo_handoff_polish(db: Session, profile_id: str = "core-risk") -> dict:
    bundle = v11_4_recovery_evidence_bundle(db, profile_id)
    walkthrough = v11_2_sample_operator_walkthrough(db, profile_id)
    data = {
        "version": "11.4",
        "mode": "final-demo-handoff-polish",
        "status": "Final demo handoff ready" if bundle["ready"] else "Final demo handoff blocked",
        "ready": bundle["ready"],
        "profile_id": profile_id,
        "demo_cards": _demo_cards(bundle, walkthrough),
        "copy_targets": _copy_targets(bundle, walkthrough),
        "operator_script": _operator_script(profile_id),
        "non_goals": _non_goals(),
    }
    data["content"] = _handoff_markdown(data)
    return data


def v11_4_operator_demo_handoff_package(db: Session, profile_id: str = "core-risk") -> dict:
    bundle = v11_4_recovery_evidence_bundle(db, profile_id)
    handoff = v11_4_final_demo_handoff_polish(db, profile_id)
    smoke_package = v11_3_operator_smoke_verification_package(db, profile_id)
    data = {
        "version": "11.4",
        "mode": "operator-demo-handoff-package",
        "status": handoff["status"],
        "ready": bundle["ready"] and handoff["ready"],
        "profile_id": profile_id,
    }
    data["content"] = (
        "\n\n".join(
            [
                "# v11.4 Operator Demo Handoff Package",
                bundle["content"],
                handoff["content"],
                smoke_package["content"],
            ]
        ).strip()
        + "\n"
    )
    return data


def _evidence_sections(snapshot: dict, fixture: dict, smoke: dict, verify: dict, conflict: dict) -> list[dict]:
    return [
        _section("rollback-snapshot", snapshot.get("ready"), True, "v10.6 rollback snapshot is exportable."),
        _section("fixture-example", fixture.get("ready"), True, "v11.1 fixture JSON can be saved."),
        _section("smoke-test", smoke.get("ready"), True, "v11.3 smoke test passes safe chain."),
        _section("post-restore-verification", verify.get("ready"), True, "v11.3 verification report is available."),
        _section(
            "digest-lock", bool(conflict.get("snapshot_digest_lock_required")), True, "v10.9 digest lock is present."
        ),
    ]


def _section(section_id: str, ready: bool, required: bool, detail: str) -> dict:
    return {"id": section_id, "ready": bool(ready), "required": required, "detail": detail}


def _demo_cards(bundle: dict, walkthrough: dict) -> list[dict]:
    return [
        {"title": "1. Show evidence", "state": bundle["status"], "copy": "v11.4 evidence bundle"},
        {"title": "2. Explain guardrails", "state": "Reset and restore use separate phrases", "copy": "v10.5 + v10.8"},
        {"title": "3. Prove lock", "state": "Digest lock required", "copy": bundle.get("snapshot_digest_lock", "")},
        {"title": "4. Walk operator", "state": walkthrough["status"], "copy": "v11.2 walkthrough"},
    ]


def _copy_targets(bundle: dict, walkthrough: dict) -> dict:
    targets = walkthrough.get("copy_targets", {})
    return {
        "snapshot_digest": bundle.get("snapshot_digest", ""),
        "snapshot_digest_lock": bundle.get("snapshot_digest_lock", ""),
        "restore_phrase": targets.get("restore_phrase", ""),
        "evidence_endpoint": "/api/release-governance/v11-4-recovery-evidence-bundle",
        "handoff_endpoint": "/api/release-governance/v11-4-final-demo-handoff-polish",
    }


def _operator_script(profile_id: str) -> list[str]:
    return [
        f"Use `{profile_id}` as the demo recovery profile.",
        "Open the v11.4 evidence bundle and confirm every required section is ready.",
        "Open the v11.4 final demo handoff and copy only the validated targets.",
        "Mention that v11.4 does not execute restore; it packages proof and handoff guidance.",
        "Run real restore only through the older guarded v10.9 endpoint when required.",
    ]


def _non_goals() -> list[str]:
    return [
        "No new destructive endpoint.",
        "No automatic restore execution.",
        "No bypass around restore phrase or digest lock.",
    ]


def _bundle_markdown(data: dict) -> str:
    lines = [
        "# v11.4 Recovery Evidence Bundle",
        "",
        f"Status: {data['status']}",
        f"Profile: {data['profile_id']}",
        f"Snapshot digest: `{data['snapshot_digest']}`",
        f"Digest lock: `{data['snapshot_digest_lock']}`",
        "",
        "## Evidence Sections",
    ]
    lines.extend(
        f"- {'READY' if item['ready'] else 'BLOCKED'}: {item['id']} — {item['detail']}"
        for item in data["evidence_sections"]
    )
    lines.append(f"\nHandoff gate: `{data['handoff_gate']}`")
    return "\n".join(lines).strip() + "\n"


def _handoff_markdown(data: dict) -> str:
    lines = [
        "# v11.4 Final Demo Handoff Polish",
        "",
        f"Status: {data['status']}",
        f"Profile: {data['profile_id']}",
        "",
        "## Demo Cards",
    ]
    lines.extend(f"- {card['title']}: {card['state']} — `{card['copy']}`" for card in data["demo_cards"])
    lines.extend(["", "## Operator Script"])
    lines.extend(f"{index}. {item}" for index, item in enumerate(data["operator_script"], start=1))
    lines.extend(["", "## Non-goals"])
    lines.extend(f"- {item}" for item in data["non_goals"])
    return "\n".join(lines).strip() + "\n"
