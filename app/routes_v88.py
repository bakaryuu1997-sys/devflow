from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.release_operator_approval_service import (
    create_final_operator_approval_record,
    create_signed_rehearsal_artifact,
    list_final_operator_approval_records,
    list_signed_rehearsal_artifacts,
    signed_rehearsal_artifact_package,
)

router = APIRouter(prefix="/api", tags=["v8-8-operator-approval"])


@router.get("/release-governance/signed-rehearsal-artifact-package")
def api_signed_rehearsal_artifact_package(db: Session = Depends(get_db)):
    return signed_rehearsal_artifact_package(db)


@router.post("/release-governance/signed-rehearsal-artifacts")
def api_create_signed_rehearsal_artifact(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    return create_signed_rehearsal_artifact(db, payload)


@router.get("/release-governance/signed-rehearsal-artifacts")
def api_list_signed_rehearsal_artifacts(db: Session = Depends(get_db)):
    return list_signed_rehearsal_artifacts(db)


@router.post("/release-governance/final-operator-approval-records")
def api_create_final_operator_approval_record(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    return create_final_operator_approval_record(db, payload)


@router.get("/release-governance/final-operator-approval-records")
def api_list_final_operator_approval_records(db: Session = Depends(get_db)):
    return list_final_operator_approval_records(db)
