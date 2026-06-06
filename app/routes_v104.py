from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.sample_project_builder_service import (
    v10_4_build_sample_project,
    v10_4_operator_sample_builder_package,
    v10_4_sample_project_builder,
    v10_4_tutorial_completion_badge,
)

router = APIRouter(prefix="/api", tags=["v10-4-sample-project-builder"])


@router.get("/release-governance/v10-4-sample-project-builder")
def api_v10_4_sample_project_builder(profile_id: str = Query(default="core-risk")):
    return v10_4_sample_project_builder(profile_id)


@router.post("/release-governance/v10-4-build-sample-project")
def api_v10_4_build_sample_project(
    profile_id: str = Query(default="core-risk"),
    operator_name: str = Query(default=""),
    db: Session = Depends(get_db),
):
    return v10_4_build_sample_project(db, profile_id, operator_name)


@router.get("/release-governance/v10-4-tutorial-completion-badge")
def api_v10_4_tutorial_completion_badge(db: Session = Depends(get_db)):
    return v10_4_tutorial_completion_badge(db)


@router.get("/release-governance/v10-4-operator-sample-builder-package")
def api_v10_4_operator_sample_builder_package(db: Session = Depends(get_db)):
    return v10_4_operator_sample_builder_package(db)
