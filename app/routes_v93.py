from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.signature_adapter_contract_service import sample_signature_fixtures, signature_adapter_contract_tests

router = APIRouter(prefix="/api", tags=["v9-3-signature-adapter-contracts"])


@router.get("/release-governance/signature-adapter-contract-tests")
def api_signature_adapter_contract_tests(db: Session = Depends(get_db)):
    return signature_adapter_contract_tests(db)


@router.get("/release-governance/sample-signature-fixtures")
def api_sample_signature_fixtures(db: Session = Depends(get_db)):
    return sample_signature_fixtures(db)
