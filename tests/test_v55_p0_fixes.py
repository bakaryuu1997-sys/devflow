from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.guard_rules import analyze_sql_migration
from app.models import Requirement, TraceLink, WorkItem
from app.traceability_service import traceability_matrix


def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_safe_delete_with_where_is_not_blocking():
    findings = analyze_sql_migration("DELETE FROM users WHERE id = 1;")

    assert not any(item["title"] == "Delete Without Where" for item in findings)


def test_delete_without_where_is_blocking():
    findings = analyze_sql_migration("DELETE FROM users;")

    assert any(item["title"] == "Delete Without Where" and item["blocking"] for item in findings)


def test_traceability_does_not_double_count_duplicate_task():
    db = session()
    req = Requirement(project_id=1, key="REQ-1", title="Login", priority="High")
    db.add(req)
    db.commit()
    db.refresh(req)
    db.add(WorkItem(project_id=1, requirement_id=req.id, kind="task", title="TASK-1", status="Done"))
    db.add(TraceLink(project_id=1, requirement_key="REQ-1", link_type="task", target_key="TASK-1", title="TASK-1"))
    db.commit()

    rows = traceability_matrix(db, 1)

    assert rows[0]["task_count"] == 1
