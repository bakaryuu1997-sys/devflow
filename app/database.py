import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


def _effective_database_url() -> str:
    """Resolve the database URL, tolerating read-only serverless filesystems.

    On platforms like Vercel the project directory is read-only (only ``/tmp``
    is writable). If we are running there with the default local SQLite path,
    relocate the file to ``/tmp`` so the app can still boot for a demo. Set a
    real ``DATABASE_URL`` (e.g. hosted Postgres) for persistent data.
    """
    url = settings.database_url
    on_serverless = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
    if on_serverless and url.startswith("sqlite") and "/tmp/" not in url:
        return "sqlite:////tmp/devflow.db"
    return url


DATABASE_URL = _effective_database_url()
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
