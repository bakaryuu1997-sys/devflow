from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.auth_mode import validate_startup_security
from app.config import settings
from app.database import Base, engine
from app.deps import require_unsafe_api_auth
from app.routes import router

validate_startup_security()
if settings.auto_create_tables:
    Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, dependencies=[Depends(require_unsafe_api_auth)])
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)


@app.get("/")
def index():
    return FileResponse("static/index.html")
