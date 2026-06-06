from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.public_key_verifier_service import (
    public_key_verifier_dry_run,
    public_key_verifier_fixture_package,
    public_key_verifier_readiness,
)

router = APIRouter(prefix="/api", tags=["v9-4-public-key-verifier"])


@router.get("/release-governance/public-key-verifier-readiness")
def api_public_key_verifier_readiness(db: Session = Depends(get_db)):
    return public_key_verifier_readiness(db)


@router.get("/release-governance/public-key-verifier-fixture-package")
def api_public_key_verifier_fixture_package(db: Session = Depends(get_db)):
    return public_key_verifier_fixture_package(db)


@router.post("/release-governance/public-key-verifier-dry-run")
def api_public_key_verifier_dry_run(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    return public_key_verifier_dry_run(db, payload)
