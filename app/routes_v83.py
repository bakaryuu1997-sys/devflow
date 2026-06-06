from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.migration_apply_assistant_service import manual_migration_apply_assistant, post_migration_verification_snapshot

router = APIRouter(prefix="/api", tags=["v8-3-manual-migration-assistant"])


@router.get("/release-governance/manual-migration-apply-assistant")
def api_manual_migration_apply_assistant(db: Session = Depends(get_db)):
    return manual_migration_apply_assistant(db)


@router.get("/release-governance/post-migration-verification-snapshot")
def api_post_migration_verification_snapshot(db: Session = Depends(get_db)):
    return post_migration_verification_snapshot(db)
