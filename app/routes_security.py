from fastapi import APIRouter

from app.auth_mode import current_auth_mode, security_checklist

router = APIRouter(prefix="/api/security", tags=["security"])


@router.get("/checklist")
def checklist():
    checks = security_checklist()
    return {
        "auth_mode": current_auth_mode(),
        "passed": all(item["passed"] or not item["blocking"] for item in checks),
        "checks": checks,
    }
