from fastapi import APIRouter

from app.usability_polish_service import (
    v10_1_operator_quickstart_package,
    v10_1_optional_deployment_guide,
    v10_1_sample_demo_script,
    v10_1_usability_walkthrough,
)

router = APIRouter(prefix="/api", tags=["v10-1-usability-polish"])


@router.get("/release-governance/v10-1-usability-walkthrough")
def api_v10_1_usability_walkthrough():
    return v10_1_usability_walkthrough()


@router.get("/release-governance/v10-1-sample-demo-script")
def api_v10_1_sample_demo_script():
    return v10_1_sample_demo_script()


@router.get("/release-governance/v10-1-optional-deployment-guide")
def api_v10_1_optional_deployment_guide():
    return v10_1_optional_deployment_guide()


@router.get("/release-governance/v10-1-operator-quickstart-package")
def api_v10_1_operator_quickstart_package():
    return v10_1_operator_quickstart_package()
