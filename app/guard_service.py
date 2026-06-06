from sqlalchemy import select
from sqlalchemy.orm import Session

from app.guard_rules import analyze_logs, analyze_openapi_diff, analyze_sql_migration, analyze_test_report
from app.models import GuardFinding


def save_findings(db: Session, project_id: int, filename: str, findings: list[dict]) -> list[GuardFinding]:
    rows = []
    for finding in findings:
        row = GuardFinding(project_id=project_id, filename=filename, **finding)
        db.add(row)
        rows.append(row)
    db.commit()
    for row in rows:
        db.refresh(row)
    return rows


def scan_sql(db: Session, project_id: int, filename: str, content: str):
    return save_findings(db, project_id, filename, analyze_sql_migration(content))


def scan_logs(db: Session, project_id: int, filename: str, content: str):
    return save_findings(db, project_id, filename, analyze_logs(content))


def scan_tests(db: Session, project_id: int, filename: str, content: str):
    return save_findings(db, project_id, filename, analyze_test_report(content))


def scan_api_diff(db: Session, project_id: int, filename: str, before: str, after: str):
    return save_findings(db, project_id, filename, analyze_openapi_diff(before, after))


def list_findings(db: Session, project_id: int):
    stmt = select(GuardFinding).where(GuardFinding.project_id == project_id).order_by(GuardFinding.id.desc())
    return list(db.scalars(stmt).all())


def blocking_guard_count(db: Session, project_id: int) -> int:
    return sum(1 for item in list_findings(db, project_id) if item.blocking)
