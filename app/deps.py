from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth_mode import is_production_mode, local_auth_disabled
from app.config import settings
from app.database import get_db
from app.models import User
from app.rbac import PERMISSION_MANAGE_USERS, PERMISSION_RELEASE, PERMISSION_WRITE, has_permission
from app.security import decode_access_token
from app.token_blacklist_service import is_token_blacklisted

# auto_error=False so requests without a token reach our handlers, which decide
# whether that is allowed (it is when local_auth_disabled() is on).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def _default_local_user(db: Session) -> User:
    """Return the account used when login is disabled for local personal use.

    Prefers an active admin, then any active user. Raises 401 if the database
    has no account yet (the launcher seeds one, so this is only a safety net).
    """
    admin = db.scalars(select(User).where(User.role == "admin", User.is_active.is_(True)).order_by(User.id)).first()
    user = admin or db.scalars(select(User).where(User.is_active.is_(True)).order_by(User.id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="No local account exists; start the app via the launcher.")
    return user


def current_user(token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    if local_auth_disabled():
        return _default_local_user(db)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token has been logged out")
    subject = decode_access_token(token)
    if not subject:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.get(User, int(subject))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive or missing user")
    return user


def require_write(user: User = Depends(current_user)) -> User:
    if not has_permission(user.role, PERMISSION_WRITE):
        raise HTTPException(status_code=403, detail="Write permission required")
    return user


def require_release(user: User = Depends(current_user)) -> User:
    if not has_permission(user.role, PERMISSION_RELEASE):
        raise HTTPException(status_code=403, detail="Release permission required")
    return user


def require_manage_users(user: User = Depends(current_user)) -> User:
    if not has_permission(user.role, PERMISSION_MANAGE_USERS):
        raise HTTPException(status_code=403, detail="Manage users permission required")
    return user


UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
PUBLIC_UNSAFE_PATHS = {"/api/auth/login", "/api/auth/register"}
LOCAL_DEMO_UNSAFE_PATHS = {"/api/demo/reset"}


def require_unsafe_api_auth(
    request: Request,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    if request.method not in UNSAFE_METHODS:
        return None
    if local_auth_disabled():
        return None

    path = request.url.path
    if path in PUBLIC_UNSAFE_PATHS:
        return None
    if path in LOCAL_DEMO_UNSAFE_PATHS and not is_production_mode() and settings.allow_demo_reset:
        return None
    if not is_production_mode() and not settings.local_write_auth_required:
        return None

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Write access requires authentication")

    token = authorization.split(" ", 1)[1].strip()
    if is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token has been logged out")

    subject = decode_access_token(token)
    if not subject:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.get(User, int(subject))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive or missing user")
    if not has_permission(user.role, PERMISSION_WRITE):
        raise HTTPException(status_code=403, detail="Write permission required")
    return user


def require_production_unsafe_api_auth(*args, **kwargs):
    return require_unsafe_api_auth(*args, **kwargs)
