from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.security import create_access_token, hash_password, verify_password


def create_user(db: Session, email: str, password: str, role: str = "admin") -> User:
    normalized_email = email.strip().lower()
    existing = db.scalars(select(User).where(User.email == normalized_email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Account already exists")

    user = User(email=normalized_email, password_hash=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    normalized_email = email.strip().lower()
    user = db.scalars(select(User).where(User.email == normalized_email)).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def token_for_user(user: User) -> str:
    return create_access_token(str(user.id))
