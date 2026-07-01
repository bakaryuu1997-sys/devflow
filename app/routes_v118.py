from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.signed_archive_handoff_service import (
    v11_8_final_user_facing_quickstart,
    v11_8_operator_checksum_quickstart_package,
    v11_8_signed_archive_checksum_handoff,
)

router = APIRouter(prefix="/api", tags=["v11-8-signed-checksum-quickstart"])


@router.get("/release-governance/v11-8-signed-archive-checksum-handoff")
def api_v11_8_signed_archive_checksum_handoff(
    profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)
):
    return v11_8_signed_archive_checksum_handoff(db, profile_id)


@router.get("/release-governance/v11-8-final-user-facing-quickstart")
def api_v11_8_final_user_facing_quickstart(profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)):
    return v11_8_final_user_facing_quickstart(db, profile_id)


@router.get("/release-governance/v11-8-operator-checksum-quickstart-package")
def api_v11_8_operator_checksum_quickstart_package(
    profile_id: str = Query(default="core-risk"), db: Session = Depends(get_db)
):
    return v11_8_operator_checksum_quickstart_package(db, profile_id)
