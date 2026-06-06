from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Project
from app.sample_project_builder_data import SAMPLE_PROFILE_SEEDS
from app.sample_project_builder_service import v10_4_build_sample_project
from app.tutorial_mode_service import v10_3_update_tutorial_step


def v10_5_profile_reset_plan(db: Session, profile_id: str = "core-risk") -> dict:
    seed = SAMPLE_PROFILE_SEEDS.get(profile_id)
    phrase = approval_phrase(profile_id)
    project = _existing_project(db, seed) if seed else None
    data = {
        "version": "10.5",
        "mode": "profile-specific-demo-reset-orchestration-plan",
        "status": "Ready" if seed else "Unknown profile",
        "ready": bool(seed),
        "profile_id": profile_id,
        "approval_phrase": phrase if seed else "",
        "target_project": seed["project"][0] if seed else "",
        "existing_project_id": project.id if project else None,
        "destructive_scope": _scope(seed),
        "orchestration_steps": _steps(seed),
        "guardrails": _guardrails(),
    }
    data["content"] = _plan_markdown(data)
    return data


def v10_5_execute_profile_reset(
    db: Session,
    profile_id: str = "core-risk",
    approval: str = "",
    operator_name: str = "",
) -> dict:
    seed = SAMPLE_PROFILE_SEEDS.get(profile_id)
    if not seed:
        return _error(profile_id, "Unknown profile")
    expected = approval_phrase(profile_id)
    if approval != expected:
        return _blocked(profile_id, expected)
    deleted = _delete_profile_project(db, seed)
    v10_3_update_tutorial_step(db, "profile", "Done", operator_name, f"Reset {profile_id}")
    built = v10_4_build_sample_project(db, profile_id, operator_name)
    data = {
        "version": "10.5",
        "mode": "profile-specific-demo-reset-execution",
        "status": "Reset complete",
        "ready": True,
        "profile_id": profile_id,
        "deleted_records": deleted,
        "project_id": built.get("project_id"),
        "completion_badge": built.get("completion_badge"),
        "approval_phrase_used": expected,
    }
    data["content"] = _result_markdown(data)
    return data


def v10_5_operator_reset_package(db: Session, profile_id: str = "core-risk") -> dict:
    plan = v10_5_profile_reset_plan(db, profile_id)
    data = {"version": "10.5", "mode": "operator-profile-reset-package", "status": plan["status"], "ready": plan["ready"]}
    data["content"] = "# v10.5 Operator Profile Reset Package\n\n" + plan["content"]
    return data


def approval_phrase(profile_id: str) -> str:
    return f"RESET DEMO PROFILE: {profile_id}"


def _existing_project(db: Session, seed: dict | None) -> Project | None:
    if not seed:
        return None
    return db.scalars(select(Project).where(Project.name == seed["project"][0])).first()


def _delete_profile_project(db: Session, seed: dict) -> dict:
    project = _existing_project(db, seed)
    if not project:
        return {"projects": 0}
    deleted: dict[str, int] = {}
    for table in reversed(Base.metadata.sorted_tables):
        if "project_id" in table.c:
            result = db.execute(delete(table).where(table.c.project_id == project.id))
            if result.rowcount:
                deleted[table.name] = result.rowcount
    result = db.execute(delete(Project).where(Project.id == project.id))
    deleted["projects"] = result.rowcount or 0
    db.commit()
    return deleted


def _scope(seed: dict | None) -> list[str]:
    if not seed:
        return []
    return [
        f"Delete only the named guided sample project: {seed['project'][0]}",
        "Delete child records that reference that project_id.",
        "Recreate deterministic requirements, work items, trace links, and release.",
        "Leave legacy /api/demo/reset behavior unchanged for old tests.",
    ]


def _steps(seed: dict | None) -> list[str]:
    if not seed:
        return ["Choose a valid demo profile first."]
    return [
        "Preview profile reset plan and current target project id.",
        "Type the exact approval phrase before execution.",
        "Delete the selected guided sample project and project-scoped child data.",
        "Run the v10.4 guided sample builder for the same profile.",
        "Mark tutorial profile and sample-builder steps as Done.",
    ]


def _guardrails() -> list[str]:
    return [
        "The reset is profile-specific and project-scoped, not a full database drop.",
        "Wrong or missing approval phrase blocks execution.",
        "Production migration approval gates remain separate from demo reset.",
    ]


def _error(profile_id: str, status: str) -> dict:
    return {"version": "10.5", "mode": "profile-specific-demo-reset-execution", "status": status, "ready": False, "profile_id": profile_id}


def _blocked(profile_id: str, expected: str) -> dict:
    data = _error(profile_id, "Approval phrase required")
    data["expected_approval_phrase"] = expected
    data["content"] = f"# v10.5 Profile Reset Blocked\n\nExpected phrase: `{expected}`\n"
    return data


def _plan_markdown(data: dict) -> str:
    lines = ["# v10.5 Profile-specific Demo Reset Plan", "", f"Status: {data['status']}", f"Profile: {data['profile_id']}", f"Approval phrase: `{data['approval_phrase']}`", "", "## Scope"]
    lines.extend(f"- {item}" for item in data["destructive_scope"])
    lines.extend(["", "## Steps"])
    lines.extend(f"{i}. {item}" for i, item in enumerate(data["orchestration_steps"], 1))
    lines.extend(["", "## Guardrails", *[f"- {item}" for item in data["guardrails"]]])
    return "\n".join(lines).strip() + "\n"


def _result_markdown(data: dict) -> str:
    return f"# v10.5 Profile Reset Result\n\nStatus: {data['status']}\nProfile: {data['profile_id']}\nProject ID: {data['project_id']}\n"
