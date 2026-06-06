from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.verifier_profile_service import create_verifier_profile, policy_presets, verifier_profile_registry

router = APIRouter(prefix="/api", tags=["v9-7-verifier-profiles"])


@router.get("/release-governance/external-verifier-profiles")
def api_verifier_profile_registry(db: Session = Depends(get_db)):
    return verifier_profile_registry(db)


@router.post("/release-governance/external-verifier-profiles")
def api_create_verifier_profile(payload: dict = Body(default={}), db: Session = Depends(get_db)):
    return create_verifier_profile(db, payload)


@router.get("/release-governance/operator-policy-presets")
def api_policy_presets():
    return policy_presets()
