from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.packaging_cleanup_service import (
    v11_6_beginner_install_verification,
    v11_6_final_packaging_cleanup,
    v11_6_operator_final_package,
)

router = APIRouter(prefix="/api", tags=["v11-6-final-packaging-install"])


@router.get("/release-governance/v11-6-final-packaging-cleanup")
def api_v11_6_final_packaging_cleanup(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_6_final_packaging_cleanup(db, profile_id)


@router.get("/release-governance/v11-6-beginner-install-verification")
def api_v11_6_beginner_install_verification(
    profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)
):
    return v11_6_beginner_install_verification(db, profile_id)


@router.get("/release-governance/v11-6-operator-final-package")
def api_v11_6_operator_final_package(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_6_operator_final_package(db, profile_id)
