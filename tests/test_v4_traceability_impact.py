from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.code_risk_service import classify_file
from app.database import Base
from app.env_guard_service import analyze_env
from app.impact_service import detect_changed_fields
from app.models import Requirement, TraceLink
from app.services import create_project
from app.traceability_service import traceability_matrix


def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_traceability_matrix_flags_missing_test():
    db = session()
    project = create_project(db, "Trace Demo")
    db.add(Requirement(project_id=project.id, key="REQ-1", title="Payment", priority="High"))
    db.commit()

    rows = traceability_matrix(db, project.id)

    assert rows[0]["risk"] == "High"


def test_traceability_counts_links():
    db = session()
    project = create_project(db, "Trace Links")
    db.add(Requirement(project_id=project.id, key="REQ-1", title="Login", priority="Medium"))
    db.add(TraceLink(project_id=project.id, requirement_key="REQ-1", link_type="api", target_key="POST /login"))
    db.commit()

    rows = traceability_matrix(db, project.id)

    assert rows[0]["api_count"] == 1


def test_detect_changed_fields_auth():
    fields = detect_changed_fields("Login by email", "Login by email or phone")

    assert "auth" in fields


def test_code_change_risk_detects_migration():
    area, severity, reason = classify_file("migrations/202606_add_user.sql")

    assert area == "database"
    assert severity == "High"


def test_env_guard_detects_debug_and_secret():
    findings = analyze_env("DATABASE_URL=x\nJWT_SECRET_KEY=change-me\nAPP_DEBUG=true")

    assert any(item["blocking"] for item in findings)
