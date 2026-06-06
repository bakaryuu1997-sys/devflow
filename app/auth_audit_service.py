from collections import defaultdict
from time import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ActivityLog

WINDOW_SECONDS = 300
MAX_FAILED_ATTEMPTS = 5
_failed_attempts: dict[str, list[float]] = defaultdict(list)


def is_login_limited(email: str) -> bool:
    key = _key(email)
    _prune(key)
    return len(_failed_attempts[key]) >= MAX_FAILED_ATTEMPTS


def record_login_failed(db: Session, email: str, reason: str = "invalid_credentials") -> None:
    key = _key(email)
    _prune(key)
    _failed_attempts[key].append(time())
    write_auth_log(db, "auth.login.failed", f"{key}: {reason}")


def record_login_success(db: Session, email: str) -> None:
    key = _key(email)
    _failed_attempts.pop(key, None)
    write_auth_log(db, "auth.login.success", key)


def record_logout(db: Session, email: str) -> None:
    write_auth_log(db, "auth.logout", _key(email))


def write_auth_log(db: Session, action: str, message: str) -> None:
    db.add(ActivityLog(project_id=None, action=action, message=message))
    db.commit()


def list_auth_logs(db: Session, limit: int = 50) -> list[ActivityLog]:
    stmt = select(ActivityLog).where(ActivityLog.action.like("auth.%")).order_by(ActivityLog.id.desc()).limit(limit)
    return list(db.scalars(stmt).all())


def reset_login_limiter() -> None:
    _failed_attempts.clear()


def _key(email: str) -> str:
    return email.strip().lower()


def _prune(key: str) -> None:
    cutoff = time() - WINDOW_SECONDS
    _failed_attempts[key] = [item for item in _failed_attempts[key] if item >= cutoff]
