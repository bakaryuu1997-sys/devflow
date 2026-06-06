from __future__ import annotations

from sqlalchemy.orm import Session

from app.end_to_end_rehearsal_service import end_to_end_governance_rehearsal
from app.final_evidence_bundle_service import final_signed_release_bundle_package
from app.verified_gate_hardening_service import verified_evidence_manifest_gate


def v10_stable_milestone_report(db: Session) -> dict:
    gate = verified_evidence_manifest_gate(db)
    bundle = final_signed_release_bundle_package(db)
    rehearsal = end_to_end_governance_rehearsal(db)
    blockers = gate["blockers"] + ([] if bundle["ready"] else ["Final evidence bundle is blocked."]) + rehearsal["blockers"]
    data = {
        "version": "10.0",
        "mode": "stable-milestone-final-qa",
        "status": "Stable Milestone Ready" if not blockers else "Stable Milestone Needs Evidence",
        "ready": not blockers,
        "blockers": sorted(set(blockers)),
        "included_versions": ["9.6", "9.7", "9.8", "9.9", "10.0"],
        "final_qa_checks": _checks(),
        "installer_steps": _installer_steps(),
    }
    data["content"] = _markdown(data)
    return data


def v10_installer_checklist() -> dict:
    data = {"version": "10.0", "mode": "installer-checklist", "steps": _installer_steps(), "status": "Ready"}
    data["content"] = "# v10.0 Installer Checklist\n\n" + "\n".join(f"- [ ] {step}" for step in data["steps"]) + "\n"
    return data


def _checks() -> list[str]:
    return ["quality_check", "compileall", "pytest grouped", "security_check", "HTTP smoke", "CLI exports", "file-size rule"]


def _installer_steps() -> list[str]:
    return ["Create virtual environment", "Install requirements", "Copy .env.example to .env", "Run migration checker", "Run rollback drill on copy", "Start uvicorn app.main:app --reload", "Open /docs and local UI"]


def _markdown(data: dict) -> str:
    lines = ["# v10.0 Stable Milestone Final QA", "", f"Status: {data['status']}", f"Ready: {data['ready']}", "", "## Blockers"]
    lines.extend(f"- {item}" for item in (data["blockers"] or ["No blockers."]))
    lines.extend(["", "## Final QA checks", *[f"- [ ] {item}" for item in data["final_qa_checks"]]])
    lines.extend(["", "## Installer steps", *[f"- [ ] {item}" for item in data["installer_steps"]]])
    return "\n".join(lines).strip() + "\n"
