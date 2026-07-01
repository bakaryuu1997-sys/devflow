import csv
import io

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import RequirementDiff


def compare_requirement_csv(db: Session, project_id: int, old_csv: str, new_csv: str) -> list[RequirementDiff]:
    old = _parse(old_csv)
    new = _parse(new_csv)
    rows = []

    for key in sorted(set(old) | set(new)):
        if key not in old:
            rows.append(_row(project_id, key, "Added", "", new[key]["title"], "", new[key]["priority"]))
        elif key not in new:
            rows.append(_row(project_id, key, "Removed", old[key]["title"], "", old[key]["priority"], ""))
        else:
            old_item = old[key]
            new_item = new[key]
            if old_item != new_item:
                rows.append(
                    _row(
                        project_id,
                        key,
                        "Changed",
                        old_item["title"],
                        new_item["title"],
                        old_item["priority"],
                        new_item["priority"],
                    )
                )

    for row in rows:
        db.add(row)
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


def list_requirement_diffs(db: Session, project_id: int) -> list[RequirementDiff]:
    stmt = select(RequirementDiff).where(RequirementDiff.project_id == project_id).order_by(RequirementDiff.id.desc())
    return list(db.scalars(stmt).all())


def _parse(content: str) -> dict:
    data = {}
    for row in csv.DictReader(io.StringIO(content)):
        key = row.get("key") or row.get("requirement_key") or row.get("id")
        if not key:
            continue
        data[key] = {
            "title": row.get("title") or row.get("name") or "",
            "priority": row.get("priority") or "Medium",
        }
    return data


def _row(project_id, key, change_type, old_title, new_title, old_priority, new_priority):
    risk = _risk(change_type, old_priority, new_priority)
    message = f"{key} {change_type.lower()}: {old_title or '-'} -> {new_title or '-'}"
    return RequirementDiff(
        project_id=project_id,
        requirement_key=key,
        change_type=change_type,
        old_title=old_title,
        new_title=new_title,
        old_priority=old_priority,
        new_priority=new_priority,
        risk=risk,
        message=message,
    )


def _risk(change_type, old_priority, new_priority) -> str:
    if change_type == "Removed":
        return "High"
    if new_priority == "Critical" or old_priority == "Critical":
        return "High"
    if change_type == "Changed":
        return "Medium"
    return "Low"
