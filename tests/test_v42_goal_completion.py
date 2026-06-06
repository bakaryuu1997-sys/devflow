from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.git_import_service import import_git_items
from app.openapi_deep_diff_service import deep_openapi_diff
from app.requirement_diff_service import compare_requirement_csv
from app.services import create_project
from app.workload_service import workload_dashboard


def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_git_import_detects_risk_and_link():
    db = session()
    project = create_project(db, "Git Demo")
    content = "ref,title,author,status,changed_files\nabc,TASK-1 auth change,Long,merged,src/auth/login.py"

    rows = import_git_items(db, project.id, content)

    assert rows[0].risk == "High"
    assert rows[0].linked_key == "TASK-1"


def test_requirement_diff_detects_removed_and_changed():
    db = session()
    project = create_project(db, "Req Diff")
    old = "key,title,priority\nREQ-1,Login,Critical\nREQ-2,PDF,High"
    new = "key,title,priority\nREQ-1,Login phone,Critical"

    rows = compare_requirement_csv(db, project.id, old, new)
    types = {row.change_type for row in rows}

    assert "Changed" in types
    assert "Removed" in types


def test_deep_openapi_detects_required_parameter():
    before = '{"paths":{"/users":{"get":{"parameters":[],"responses":{"200":{}}}}}}'
    after = '{"paths":{"/users":{"get":{"parameters":[{"name":"phone","required":true}],"responses":{"200":{}}}}}}'

    findings = deep_openapi_diff(before, after)

    assert findings[0]["blocking"] is True


def test_workload_dashboard_returns_rows_for_git_owner():
    db = session()
    project = create_project(db, "Workload")
    content = "ref,title,author,status,changed_files\nabc,TASK-1 payment change,Ana,merged,src/payment/service.py"
    import_git_items(db, project.id, content)

    rows = workload_dashboard(db, project.id)

    assert rows[0]["owner"] == "Ana"
    assert rows[0]["risk"] in {"High", "Critical"}
