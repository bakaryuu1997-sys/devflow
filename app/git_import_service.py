import csv
import io
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.code_risk_service import classify_file
from app.models import GitItem, TraceLink

KEY_RE = re.compile(r"\b(REQ|TASK|BUG)-[A-Za-z0-9_-]+\b")


def import_git_items(db: Session, project_id: int, content: str, item_type: str = "commit") -> list[GitItem]:
    rows = []
    reader = csv.DictReader(io.StringIO(content))
    for raw in reader:
        title = raw.get("title") or raw.get("message") or ""
        changed_files = raw.get("changed_files") or raw.get("files") or ""
        linked_key = _extract_key(title)
        risk = _risk_from_files(changed_files)
        item = GitItem(
            project_id=project_id,
            item_type=item_type,
            ref=raw.get("ref") or raw.get("sha") or raw.get("id") or "",
            title=title,
            author=raw.get("author") or raw.get("owner") or "",
            status=raw.get("status") or raw.get("state") or "",
            changed_files=changed_files,
            linked_key=linked_key,
            risk=risk,
        )
        db.add(item)
        rows.append(item)
        if linked_key:
            db.add(
                TraceLink(
                    project_id=project_id,
                    requirement_key=_requirement_key(linked_key),
                    link_type="commit" if item_type == "commit" else "pr",
                    target_key=item.ref,
                    title=title,
                    status=item.status,
                    module="git",
                )
            )
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


def list_git_items(db: Session, project_id: int) -> list[GitItem]:
    stmt = select(GitItem).where(GitItem.project_id == project_id).order_by(GitItem.id.desc())
    return list(db.scalars(stmt).all())


def _extract_key(text: str) -> str:
    match = KEY_RE.search(text or "")
    return match.group(0) if match else ""


def _requirement_key(key: str) -> str:
    return key if key.startswith("REQ-") else "REQ-001"


def _risk_from_files(changed_files: str) -> str:
    severities = []
    for file_path in re.split(r"[;\n,]+", changed_files or ""):
        _, severity, _ = classify_file(file_path.strip())
        severities.append(severity)
    if "Critical" in severities:
        return "Critical"
    if "High" in severities:
        return "High"
    if "Medium" in severities:
        return "Medium"
    return "Low"
