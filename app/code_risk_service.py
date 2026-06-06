from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CodeChange


RULES = [
    ("database", ["migration", "alembic", ".sql"], "High", "Database schema/data may change."),
    ("auth", ["auth", "login", "token", "session", "permission"], "High", "Authentication or permission logic changed."),
    ("payment", ["payment", "invoice", "billing", "checkout"], "Critical", "Payment flow changed."),
    ("config", [".env", "settings", "config", "secret"], "High", "Configuration or secret-sensitive file changed."),
    ("api", ["routes", "api", "schema", "openapi"], "Medium", "API contract may change."),
    ("frontend", ["component", "page", "form", ".tsx", ".jsx"], "Medium", "User-facing UI changed."),
    ("style", [".css", ".scss"], "Low", "Styling-only change."),
]


def analyze_code_changes(db: Session, project_id: int, payload) -> list[CodeChange]:
    rows = []
    for file_path in payload.files:
        area, severity, reason = classify_file(file_path)
        row = CodeChange(
            project_id=project_id,
            source=payload.source,
            file_path=file_path,
            area=area,
            severity=severity,
            reason=reason,
        )
        db.add(row)
        rows.append(row)
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


def list_code_changes(db: Session, project_id: int) -> list[CodeChange]:
    stmt = select(CodeChange).where(CodeChange.project_id == project_id).order_by(CodeChange.id.desc())
    return list(db.scalars(stmt).all())


def classify_file(file_path: str) -> tuple[str, str, str]:
    lowered = file_path.lower()
    for area, needles, severity, reason in RULES:
        if any(needle in lowered for needle in needles):
            return area, severity, reason
    return "general", "Low", "General code change."
