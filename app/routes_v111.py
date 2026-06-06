from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.recovery_ux_fixture_service import (
    v11_1_export_fixture_example,
    v11_1_import_fixture_example,
    v11_1_operator_fixture_package,
    v11_1_recovery_ux_summary,
)

router = APIRouter(prefix="/api", tags=["v11-1-recovery-ux-fixtures"])


@router.get("/release-governance/v11-1-recovery-ux-summary")
def api_v11_1_recovery_ux_summary(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_1_recovery_ux_summary(db, profile_id)


@router.get("/release-governance/v11-1-export-fixture-example")
def api_v11_1_export_fixture_example(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_1_export_fixture_example(db, profile_id)


@router.post("/release-governance/v11-1-import-fixture-example")
def api_v11_1_import_fixture_example(
    profile_id: str = Query(default="core-risk"),
    fixture_payload: dict | None = Body(default=None),
    db: Session = Depends(get_db),
):
    return v11_1_import_fixture_example(db, profile_id, fixture_payload)


@router.get("/release-governance/v11-1-operator-fixture-package")
def api_v11_1_operator_fixture_package(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_1_operator_fixture_package(db, profile_id)
