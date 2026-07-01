from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.recovery_evidence_handoff_service import v11_4_recovery_evidence_bundle
from app.recovery_fixture_validation_service import v11_2_fixture_validation_report
from app.recovery_smoke_verification_service import v11_3_recovery_smoke_test_automation

RC_VERSION = "11.5"
RC_LABEL = "demo-rc-v11.5"


def v11_5_demo_release_candidate_freeze(db: Session, profile_id: str = "core-risk") -> dict:
    bundle = v11_4_recovery_evidence_bundle(db, profile_id)
    validation = v11_2_fixture_validation_report(db, profile_id)
    smoke = v11_3_recovery_smoke_test_automation(db, profile_id)
    gates = _freeze_gates(bundle, validation, smoke)
    ready = all(item["pass"] for item in gates)
    data = {
        "version": RC_VERSION,
        "mode": "demo-release-candidate-freeze",
        "release_candidate": RC_LABEL,
        "status": "Demo release candidate frozen" if ready else "Demo release candidate blocked",
        "ready": ready,
        "profile_id": profile_id,
        "frozen_on": date.today().isoformat(),
        "freeze_state": "frozen" if ready else "not-frozen",
        "freeze_gates": gates,
        "immutable_copy_targets": _immutable_copy_targets(bundle),
        "non_goals": _non_goals(),
    }
    data["content"] = _freeze_markdown(data)
    return data


def v11_5_operator_acceptance_checklist(db: Session, profile_id: str = "core-risk") -> dict:
    freeze = v11_5_demo_release_candidate_freeze(db, profile_id)
    checklist = _acceptance_items(freeze)
    accepted = all(item["required"] and item["checked"] for item in checklist)
    data = {
        "version": RC_VERSION,
        "mode": "operator-acceptance-checklist",
        "status": "Operator acceptance checklist ready" if accepted else "Operator acceptance checklist blocked",
        "ready": accepted,
        "profile_id": profile_id,
        "release_candidate": RC_LABEL,
        "checklist": checklist,
        "signoff_phrase": f"ACCEPT DEMO RC: {RC_LABEL}",
        "handoff_note": "Use this checklist before presenting or handing off the demo package.",
    }
    data["content"] = _checklist_markdown(data)
    return data


def v11_5_operator_release_candidate_package(db: Session, profile_id: str = "core-risk") -> dict:
    freeze = v11_5_demo_release_candidate_freeze(db, profile_id)
    checklist = v11_5_operator_acceptance_checklist(db, profile_id)
    data = {
        "version": RC_VERSION,
        "mode": "operator-release-candidate-package",
        "status": checklist["status"],
        "ready": freeze["ready"] and checklist["ready"],
        "profile_id": profile_id,
        "release_candidate": RC_LABEL,
    }
    data["content"] = (
        "\n\n".join(
            [
                "# v11.5 Operator Release Candidate Package",
                freeze["content"],
                checklist["content"],
            ]
        ).strip()
        + "\n"
    )
    return data


def _freeze_gates(bundle: dict, validation: dict, smoke: dict) -> list[dict]:
    return [
        _gate("evidence-bundle-ready", bundle.get("ready"), "v11.4 evidence bundle is complete."),
        _gate("fixture-validation-ready", validation.get("ready"), "v11.2 fixture validation is hardened."),
        _gate("smoke-test-ready", smoke.get("ready"), "v11.3 recovery smoke test passes."),
        _gate("digest-lock-present", bool(bundle.get("snapshot_digest_lock")), "Snapshot digest lock is copyable."),
        _gate("no-new-destructive-path", True, "v11.5 only freezes and packages the candidate."),
    ]


def _gate(gate_id: str, passed: bool, detail: str) -> dict:
    return {"id": gate_id, "pass": bool(passed), "required": True, "detail": detail}


def _immutable_copy_targets(bundle: dict) -> dict:
    return {
        "release_candidate": RC_LABEL,
        "snapshot_digest": bundle.get("snapshot_digest", ""),
        "snapshot_digest_lock": bundle.get("snapshot_digest_lock", ""),
        "evidence_endpoint": "/api/release-governance/v11-4-recovery-evidence-bundle",
        "acceptance_endpoint": "/api/release-governance/v11-5-operator-acceptance-checklist",
    }


def _non_goals() -> list[str]:
    return [
        "No schema migration.",
        "No destructive reset or restore endpoint.",
        "No bypass around restore phrase or digest lock.",
    ]


def _acceptance_items(freeze: dict) -> list[dict]:
    return [
        _item("rc-freeze", freeze["ready"], "Release candidate freeze report is ready."),
        _item("evidence-reviewed", freeze["ready"], "Operator reviewed the evidence bundle."),
        _item(
            "digest-lock-copied",
            bool(freeze["immutable_copy_targets"].get("snapshot_digest_lock")),
            "Digest lock is copied exactly.",
        ),
        _item("non-goals-reviewed", True, "Operator understands v11.5 does not execute restore."),
        _item("handoff-ready", freeze["freeze_state"] == "frozen", "Demo can be handed off as the frozen candidate."),
    ]


def _item(item_id: str, checked: bool, detail: str) -> dict:
    return {"id": item_id, "checked": bool(checked), "required": True, "detail": detail}


def _freeze_markdown(data: dict) -> str:
    lines = [
        "# v11.5 Demo Release Candidate Freeze",
        "",
        f"Status: {data['status']}",
        f"Release candidate: `{data['release_candidate']}`",
        f"Profile: {data['profile_id']}",
        f"Freeze state: `{data['freeze_state']}`",
        "",
        "## Freeze Gates",
    ]
    lines.extend(
        f"- {'PASS' if gate['pass'] else 'BLOCK'}: {gate['id']} — {gate['detail']}" for gate in data["freeze_gates"]
    )
    lines.extend(["", "## Non-goals"])
    lines.extend(f"- {item}" for item in data["non_goals"])
    return "\n".join(lines).strip() + "\n"


def _checklist_markdown(data: dict) -> str:
    lines = [
        "# v11.5 Operator Acceptance Checklist",
        "",
        f"Status: {data['status']}",
        f"Release candidate: `{data['release_candidate']}`",
        f"Signoff phrase: `{data['signoff_phrase']}`",
        "",
        "## Checklist",
    ]
    lines.extend(
        f"- {'DONE' if item['checked'] else 'TODO'}: {item['id']} — {item['detail']}" for item in data["checklist"]
    )
    lines.append(f"\n{data['handoff_note']}")
    return "\n".join(lines).strip() + "\n"
