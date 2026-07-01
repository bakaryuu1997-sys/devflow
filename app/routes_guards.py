from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_write
from app.evidence_service import build_evidence_markdown
from app.guard_service import list_findings, scan_api_diff, scan_logs, scan_sql, scan_tests
from app.models import User
from app.schemas import EvidenceRead, GuardFindingRead

router = APIRouter(prefix="/api/projects/{project_id}", tags=["guards"])


@router.post("/guards/sql", response_model=list[GuardFindingRead])
async def upload_sql(
    project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), _user: User = Depends(require_write)
):
    content = (await file.read()).decode("utf-8", errors="ignore")
    return scan_sql(db, project_id, file.filename or "migration.sql", content)


@router.post("/guards/logs", response_model=list[GuardFindingRead])
async def upload_logs(
    project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), _user: User = Depends(require_write)
):
    content = (await file.read()).decode("utf-8", errors="ignore")
    return scan_logs(db, project_id, file.filename or "app.log", content)


@router.post("/guards/tests", response_model=list[GuardFindingRead])
async def upload_tests(
    project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), _user: User = Depends(require_write)
):
    content = (await file.read()).decode("utf-8", errors="ignore")
    return scan_tests(db, project_id, file.filename or "test-report.xml", content)


@router.post("/guards/api-diff", response_model=list[GuardFindingRead])
async def upload_api_diff(
    project_id: int,
    before: UploadFile = File(...),
    after: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user: User = Depends(require_write),
):
    before_content = (await before.read()).decode("utf-8", errors="ignore")
    after_content = (await after.read()).decode("utf-8", errors="ignore")
    return scan_api_diff(db, project_id, before.filename or "before.json", before_content, after_content)


@router.get("/guards", response_model=list[GuardFindingRead])
def guards(project_id: int, db: Session = Depends(get_db)):
    return list_findings(db, project_id)


@router.get("/evidence", response_model=EvidenceRead)
def evidence(project_id: int, release_id: int | None = None, db: Session = Depends(get_db)):
    return {
        "project_id": project_id,
        "release_id": release_id,
        "content": build_evidence_markdown(db, project_id, release_id),
    }


@router.get("/evidence.md")
def evidence_markdown(project_id: int, release_id: int | None = None, db: Session = Depends(get_db)):
    return PlainTextResponse(build_evidence_markdown(db, project_id, release_id), media_type="text/markdown")
