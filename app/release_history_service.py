from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project, ReleaseRetrospective, ReleaseSignOff
from app.release_snapshot_service import snapshot_from_signoff

REQ_ROW_RE = re.compile(r"^- \[[ x]\] (?P<key>[^—|]+) — (?P<title>.*?) \|", re.MULTILINE)


def compare_release_signoffs(
    db: Session, project_id: int, base_id: int | None = None, target_id: int | None = None
) -> dict:
    signoffs = _project_signoffs(db, project_id)
    if len(signoffs) < 2 and not (base_id and target_id):
        return {
            "project_id": project_id,
            "can_compare": False,
            "message": "At least two approval records are needed before history compare is useful.",
            "records_available": [_signoff_summary(row) for row in signoffs],
            "summary_markdown": "No comparison available yet. Create at least two final approval records first.\n",
        }
    base = db.get(ReleaseSignOff, base_id) if base_id else signoffs[1]
    target = db.get(ReleaseSignOff, target_id) if target_id else signoffs[0]
    if not base or not target or base.project_id != project_id or target.project_id != project_id:
        return {
            "project_id": project_id,
            "can_compare": False,
            "message": "Selected approval records do not belong to this project.",
            "records_available": [_signoff_summary(row) for row in signoffs],
            "summary_markdown": "Selected approval records are invalid for this project.\n",
        }
    base_rows = _approval_rows_from_snapshot(base)
    target_rows = _approval_rows_from_snapshot(target)
    base_keys = set(base_rows)
    target_keys = set(target_rows)
    comparison = {
        "project_id": project_id,
        "can_compare": True,
        "base": _signoff_summary(base),
        "target": _signoff_summary(target),
        "version_changed": base.release_version != target.release_version,
        "approver_changed": base.approved_by != target.approved_by,
        "note_changed": (base.approval_note or "") != (target.approval_note or ""),
        "added_requirements": [_row_dict(key, target_rows[key]) for key in sorted(target_keys - base_keys)],
        "removed_requirements": [_row_dict(key, base_rows[key]) for key in sorted(base_keys - target_keys)],
        "unchanged_requirements": [_row_dict(key, target_rows[key]) for key in sorted(target_keys & base_keys)],
        "records_available": [_signoff_summary(row) for row in signoffs],
    }
    comparison["summary_markdown"] = _compare_markdown(comparison)
    return comparison


def create_retrospective_note(
    db: Session,
    project_id: int,
    signoff_id: int | None,
    author: str,
    what_went_well: str,
    what_to_improve: str,
    action_items: str,
) -> dict:
    project = db.get(Project, project_id)
    signoff = db.get(ReleaseSignOff, signoff_id) if signoff_id else None
    if signoff_id and (not signoff or signoff.project_id != project_id):
        return {"created": False, "message": "Selected sign-off record does not belong to this project."}
    note = ReleaseRetrospective(
        project_id=project_id,
        signoff_id=signoff_id,
        author=author.strip() or "Release owner",
        what_went_well=what_went_well.strip(),
        what_to_improve=what_to_improve.strip(),
        action_items=action_items.strip(),
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return {
        "created": True,
        "message": "Post-release retrospective note saved.",
        "note": _retrospective_dict(note),
        "content": retrospective_markdown(project.name if project else "Unknown project", note, signoff),
    }


def list_retrospective_notes(db: Session, project_id: int) -> list[dict]:
    notes = db.scalars(
        select(ReleaseRetrospective)
        .where(ReleaseRetrospective.project_id == project_id)
        .order_by(ReleaseRetrospective.created_at.desc())
    ).all()
    return [_retrospective_dict(note) for note in notes]


def export_retrospective_note(db: Session, note_id: int) -> dict | None:
    note = db.get(ReleaseRetrospective, note_id)
    if not note:
        return None
    project = db.get(Project, note.project_id)
    signoff = db.get(ReleaseSignOff, note.signoff_id) if note.signoff_id else None
    data = _retrospective_dict(note)
    data["content"] = retrospective_markdown(project.name if project else "Unknown project", note, signoff)
    return data


def retrospective_markdown(project_name: str, note: ReleaseRetrospective, signoff: ReleaseSignOff | None) -> str:
    release = signoff.release_version if signoff else "unassigned"
    return "\n".join(
        [
            "# Post-release Retrospective Note",
            "",
            f"Project: {project_name} (#{note.project_id})",
            f"Release: {release}",
            f"Author: {note.author}",
            f"Created at: {note.created_at.isoformat() if note.created_at else ''}",
            "",
            "## What went well",
            note.what_went_well or "No note provided.",
            "",
            "## What to improve",
            note.what_to_improve or "No note provided.",
            "",
            "## Action items",
            note.action_items or "No action items recorded.",
            "",
        ]
    )


def _project_signoffs(db: Session, project_id: int) -> list[ReleaseSignOff]:
    return list(
        db.scalars(
            select(ReleaseSignOff)
            .where(ReleaseSignOff.project_id == project_id)
            .order_by(ReleaseSignOff.created_at.desc())
        ).all()
    )


def legacy_approval_rows(snapshot: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for match in REQ_ROW_RE.finditer(snapshot or ""):
        key = match.group("key").strip()
        rows[key] = match.group("title").strip()
    return rows


def _approval_rows_from_snapshot(signoff: ReleaseSignOff) -> dict[str, str]:
    snapshot = snapshot_from_signoff(signoff)
    rows: dict[str, str] = {}
    for req in snapshot.get("requirements", []) or []:
        key = (req.get("key") or req.get("requirement_key") or "").strip()
        title = (req.get("title") or req.get("requirement_title") or "").strip()
        if key:
            rows[key] = title
    if rows:
        return rows
    return legacy_approval_rows(signoff.snapshot)


def _row_dict(key: str, title: str) -> dict:
    return {"requirement_key": key, "requirement_title": title}


def _signoff_summary(signoff: ReleaseSignOff) -> dict:
    return {
        "id": signoff.id,
        "release_version": signoff.release_version,
        "approved_by": signoff.approved_by,
        "approval_note": signoff.approval_note,
        "created_at": signoff.created_at.isoformat() if signoff.created_at else None,
    }


def _retrospective_dict(note: ReleaseRetrospective) -> dict:
    return {
        "id": note.id,
        "project_id": note.project_id,
        "signoff_id": note.signoff_id,
        "author": note.author,
        "what_went_well": note.what_went_well,
        "what_to_improve": note.what_to_improve,
        "action_items": note.action_items,
        "created_at": note.created_at.isoformat() if note.created_at else None,
    }


def _compare_markdown(data: dict) -> str:
    base = data["base"]
    target = data["target"]
    lines = [
        "# Release Approval History Compare",
        "",
        f"Base: {base['release_version']} · {base['created_at']} · {base['approved_by']}",
        f"Target: {target['release_version']} · {target['created_at']} · {target['approved_by']}",
        "",
        "## Summary",
        f"- Version changed: {data['version_changed']}",
        f"- Approver changed: {data['approver_changed']}",
        f"- Approval note changed: {data['note_changed']}",
        f"- Added requirements: {len(data['added_requirements'])}",
        f"- Removed requirements: {len(data['removed_requirements'])}",
        f"- Unchanged requirements: {len(data['unchanged_requirements'])}",
        "",
        "## Added requirements",
    ]
    lines.extend(_requirement_lines(data["added_requirements"]))
    lines.extend(["", "## Removed requirements"])
    lines.extend(_requirement_lines(data["removed_requirements"]))
    lines.extend(["", "## Unchanged requirements"])
    lines.extend(_requirement_lines(data["unchanged_requirements"]))
    return "\n".join(lines).strip() + "\n"


def _requirement_lines(rows: list[dict]) -> list[str]:
    return [f"- {row['requirement_key']} — {row['requirement_title']}" for row in rows] or ["- None"]
