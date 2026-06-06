from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth_audit_service import (
    is_login_limited,
    list_auth_logs,
    record_login_failed,
    record_login_success,
    record_logout,
)
from app.auth_service import authenticate, create_user, token_for_user
from app.config import settings
from app.database import get_db
from app.deps import current_user, oauth2_scheme, require_manage_users
from app.models import User
from app.rbac import ROLE_VIEWER
from app.token_blacklist_service import blacklist_token
from app.schemas import ActivityRead, LoginRequest, TokenRead, UserCreate, UserRead

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if not settings.allow_public_register:
        raise HTTPException(status_code=403, detail="Public registration is disabled")
    return create_user(db, payload.email, payload.password, ROLE_VIEWER)


@router.post("/login", response_model=TokenRead)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if is_login_limited(email):
        record_login_failed(db, email, "rate_limited")
        raise HTTPException(status_code=429, detail="Too many failed login attempts")

    user = authenticate(db, email, payload.password)
    if not user:
        record_login_failed(db, email)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    record_login_success(db, email)
    return {"access_token": token_for_user(user), "token_type": "bearer"}


@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme), user: User = Depends(current_user), db: Session = Depends(get_db)):
    blacklist_token(token)
    record_logout(db, user.email)
    return {"message": "Logged out"}


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(current_user)):
    return user


@router.get("/audit", response_model=list[ActivityRead])
def audit(db: Session = Depends(get_db), _user: User = Depends(require_manage_users)):
    return list_auth_logs(db)
