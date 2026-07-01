from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.final_release_tag_service import (
    v11_9_final_release_tag_preparation,
    v11_9_operator_final_release_package,
    v11_9_portfolio_demo_script,
)

router = APIRouter(prefix="/api", tags=["v11-9-final-release-tag-portfolio"])


@router.get("/release-governance/v11-9-final-release-tag-preparation")
def api_v11_9_final_release_tag_preparation(
    profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)
):
    return v11_9_final_release_tag_preparation(db, profile_id)


@router.get("/release-governance/v11-9-portfolio-demo-script")
def api_v11_9_portfolio_demo_script(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_9_portfolio_demo_script(db, profile_id)


@router.get("/release-governance/v11-9-operator-final-release-package")
def api_v11_9_operator_final_release_package(
    profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)
):
    return v11_9_operator_final_release_package(db, profile_id)
