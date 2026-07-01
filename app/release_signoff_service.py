from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project, Release, ReleaseSignOff
from app.release_completion_service import project_release_review_completion
from app.release_review_checklist_service import release_review_checklist
from app.release_risk_dashboard_service import release_risk_dashboard
from app.release_snapshot_service import (
    attach_structured_snapshot,
    build_structured_snapshot,
    snapshot_from_signoff,
    snapshot_to_json,
)
from app.time_utils import utc_now


def release_signoff_snapshot(db: Session, project_id: int) -> dict:
    project = db.get(Project, project_id)
    latest_release = _latest_release(db, project_id)
    completion = project_release_review_completion(db, project_id)
    risk_dashboard = release_risk_dashboard(db, project_id)
    checklist = release_review_checklist(db, project_id)
    ready = bool(completion["release_review_complete"] and risk_dashboard["blocking_risks"] == 0)
    return attach_structured_snapshot({
        "project_id": project_id,
        "project_name": project.name if project else "Unknown project",
        "release_id": latest_release.id if latest_release else None,
        "release_version": latest_release.version if latest_release else "unassigned",
        "generated_at": utc_now().isoformat(),
        "ready_for_signoff": ready,
        "decision": "APPROVE" if ready else "WAIT",
        "completion": completion,
        "risk_dashboard": risk_dashboard,
        "checklist_markdown": checklist["content"],
        "signoff_blockers": _signoff_blockers(completion, risk_dashboard),
    })


def create_release_signoff(db: Session, project_id: int, approved_by: str, approval_note: str = "") -> dict:
    snapshot = release_signoff_snapshot(db, project_id)
    if not snapshot["ready_for_signoff"]:
        return {
            "created": False,
            "message": "Release cannot be signed off until review completion passes and blocking risks are zero.",
            "snapshot": snapshot,
        }
    structured = build_structured_snapshot(snapshot, approved_by, approval_note)
    signoff = ReleaseSignOff(
        project_id=project_id,
        release_id=snapshot["release_id"],
        release_version=snapshot["release_version"],
        approved_by=approved_by.strip() or "Release owner",
        approval_note=approval_note.strip(),
        snapshot=_approval_record_markdown(snapshot, approved_by, approval_note, utc_now()),
        snapshot_json=snapshot_to_json(structured),
    )
    db.add(signoff)
    db.commit()
    db.refresh(signoff)
    return {
        "created": True,
        "message": "Final release sign-off snapshot created.",
        "signoff": _signoff_dict(signoff),
        "approval_record": signoff.snapshot,
    }


def list_release_signoffs(db: Session, project_id: int) -> list[dict]:
    signoffs = db.scalars(
        select(ReleaseSignOff).where(ReleaseSignOff.project_id == project_id).order_by(ReleaseSignOff.created_at.desc())
    ).all()
    return [_signoff_dict(signoff) for signoff in signoffs]


def approval_record(db: Session, signoff_id: int) -> dict | None:
    signoff = db.get(ReleaseSignOff, signoff_id)
    if not signoff:
        return None
    data = _signoff_dict(signoff)
    data["content"] = signoff.snapshot
    data["structured_snapshot"] = snapshot_from_signoff(signoff)
    return data


def _latest_release(db: Session, project_id: int) -> Release | None:
    return db.scalars(select(Release).where(Release.project_id == project_id).order_by(Release.id.desc())).first()


def _signoff_blockers(completion: dict, risk_dashboard: dict) -> list[str]:
    blockers: list[str] = []
    if completion["total_requirements"] == 0:
        blockers.append("No active requirements are available for release review.")
    if completion["done_requirements"] != completion["total_requirements"]:
        blockers.append("Not all active requirements have passed done gates.")
    if completion["reviewed_requirements"] != completion["total_requirements"]:
        blockers.append("Not all active requirements are marked review complete.")
    if completion["blocking_requirements"]:
        blockers.append("Some requirements still have blocking release-review gates.")
    if risk_dashboard["blocking_risks"]:
        blockers.append("Release risk dashboard still contains blocking risks.")
    return blockers


def _approval_record_markdown(snapshot: dict, approved_by: str, approval_note: str, created_at: datetime) -> str:
    completion = snapshot["completion"]
    risk = snapshot["risk_dashboard"]
    lines = [
        "# Final Release Sign-off Approval Record",
        "",
        f"Generated at: {created_at.isoformat()}",
        f"Project: {snapshot['project_name']} (#{snapshot['project_id']})",
        f"Release: {snapshot['release_version']}",
        f"Approved by: {approved_by.strip() or 'Release owner'}",
        f"Decision: {'APPROVED' if snapshot['ready_for_signoff'] else 'WAIT'}",
        "",
        "## Approval note",
        approval_note.strip() or "No additional note provided.",
        "",
        "## Snapshot summary",
        f"- Review completion: {completion['reviewed_requirements']}/{completion['total_requirements']} requirements reviewed",
        f"- Done gates: {completion['done_requirements']}/{completion['total_requirements']} requirements passed",
        f"- Blocking requirements: {completion['blocking_requirements']}",
        f"- Total risks: {risk['total_risks']}",
        f"- Blocking risks: {risk['blocking_risks']}",
        f"- Release status: {risk['release_status']}",
        "",
        "## Requirement approval rows",
    ]
    for row in completion.get("requirements", []):
        mark = "x" if row["is_done"] and row["review_complete"] else " "
        lines.append(
            f"- [{mark}] {row['requirement_key']} — {row['requirement_title']} | "
            f"done={row['is_done']} | reviewed={row['review_complete']} | blocking_risks={row['blocking_risks']}"
        )
    if not completion.get("requirements"):
        lines.append("- [ ] No active requirements were reviewed.")
    lines.extend(["", "## Export checklist snapshot", snapshot["checklist_markdown"].strip()])
    return "\n".join(lines).strip() + "\n"


def _signoff_dict(signoff: ReleaseSignOff) -> dict:
    return {
        "id": signoff.id,
        "project_id": signoff.project_id,
        "release_id": signoff.release_id,
        "release_version": signoff.release_version,
        "approved_by": signoff.approved_by,
        "approval_note": signoff.approval_note,
        "created_at": signoff.created_at.isoformat() if signoff.created_at else None,
        "has_structured_snapshot": bool(signoff.snapshot_json),
    }
