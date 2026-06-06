from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.recovery_fixture_validation_service import (
    v11_2_fixture_validation_report,
    v11_2_operator_walkthrough_package,
    v11_2_sample_operator_walkthrough,
)

router = APIRouter(prefix="/api", tags=["v11-2-recovery-fixture-validation"])


@router.post("/release-governance/v11-2-fixture-validation-report")
def api_v11_2_fixture_validation_report(
    profile_id: str = Query(default="core-risk"),
    fixture_payload: dict | None = Body(default=None),
    db: Session = Depends(get_db),
):
    return v11_2_fixture_validation_report(db, profile_id, fixture_payload)


@router.get("/release-governance/v11-2-sample-operator-walkthrough")
def api_v11_2_sample_operator_walkthrough(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_2_sample_operator_walkthrough(db, profile_id)


@router.get("/release-governance/v11-2-operator-walkthrough-package")
def api_v11_2_operator_walkthrough_package(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_2_operator_walkthrough_package(db, profile_id)
