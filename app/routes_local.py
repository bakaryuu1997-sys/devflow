"""Local data-management endpoints for personal/offline use.

Exposes lightweight stats, a SQLite backup download, and a full reset. All of
it is disabled in production so it can never touch a hosted deployment.
"""

from __future__ import annotations

import datetime as _dt

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import seed
from app.auth_mode import is_production_mode
from app.database import DATABASE_URL, Base, engine, get_db

router = APIRouter(prefix="/api/local", tags=["local"])


def _guard_local() -> None:
    if is_production_mode():
        raise HTTPException(status_code=403, detail="Local data management is disabled in production")


def _sqlite_path() -> str:
    if not DATABASE_URL.startswith("sqlite"):
        raise HTTPException(status_code=400, detail="Backup is only available for the local SQLite database")
    # sqlite:///relative or sqlite:////absolute -> strip the scheme prefix.
    return DATABASE_URL.replace("sqlite:///", "", 1)


@router.get("/stats")
def local_stats(db: Session = Depends(get_db)) -> dict:
    _guard_local()
    counts = {
        name: db.scalar(select(func.count()).select_from(table)) or 0 for name, table in Base.metadata.tables.items()
    }
    return {
        "database_url": DATABASE_URL,
        "total_rows": sum(counts.values()),
        "tables": counts,
    }


@router.get("/backup")
def local_backup() -> FileResponse:
    _guard_local()
    path = _sqlite_path()
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return FileResponse(path, media_type="application/octet-stream", filename=f"devflow-backup-{stamp}.db")


@router.post("/reset-all")
def local_reset_all() -> dict:
    """Drop every table, recreate the schema, and re-seed the default admin."""
    _guard_local()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed.main()
    return {"status": "reset", "message": "All local data cleared; default admin re-seeded."}
