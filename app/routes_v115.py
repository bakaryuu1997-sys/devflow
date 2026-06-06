from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.demo_release_candidate_service import (
    v11_5_demo_release_candidate_freeze,
    v11_5_operator_acceptance_checklist,
    v11_5_operator_release_candidate_package,
)

router = APIRouter(prefix="/api", tags=["v11-5-demo-release-candidate"])


@router.get("/release-governance/v11-5-demo-release-candidate-freeze")
def api_v11_5_demo_release_candidate_freeze(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_5_demo_release_candidate_freeze(db, profile_id)


@router.get("/release-governance/v11-5-operator-acceptance-checklist")
def api_v11_5_operator_acceptance_checklist(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_5_operator_acceptance_checklist(db, profile_id)


@router.get("/release-governance/v11-5-operator-release-candidate-package")
def api_v11_5_operator_release_candidate_package(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_5_operator_release_candidate_package(db, profile_id)
