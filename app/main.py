from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.auth_mode import validate_startup_security
from app.config import settings
from app.database import Base, engine
from app.deps import require_unsafe_api_auth
from app.routes import router

# Absolute paths so static assets resolve regardless of the process working
# directory (important on serverless hosts where the CWD is not the repo root).
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

validate_startup_security()
if settings.auto_create_tables:
    Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, dependencies=[Depends(require_unsafe_api_auth)])
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(router)


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/workspace")
@app.get("/workspace/")
def workspace():
    return FileResponse(STATIC_DIR / "workspace.html")
