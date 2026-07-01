from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Project, Release, Requirement, User, WorkItem

DEMO_RESET_APPROVAL = "I_UNDERSTAND_DEMO_RESET_WILL_REBUILD_LOCAL_DEMO_DATA"


def v10_2_first_run_wizard(db: Session) -> dict:
    inventory = _workspace_inventory(db)
    steps = _wizard_steps(inventory)
    blockers = [step["name"] for step in steps if step["status"] == "Blocked"]
    data = {
        "version": "10.2",
        "mode": "guided-first-run-wizard",
        "status": "Ready" if not blockers else "Action Needed",
        "ready": not blockers,
        "workspace_inventory": inventory,
        "steps": steps,
        "next_safe_action": _next_safe_action(steps),
        "safety_notes": _safety_notes(),
    }
    data["content"] = _wizard_markdown(data)
    return data


def v10_2_demo_reset_safety_check(db: Session) -> dict:
    inventory = _workspace_inventory(db)
    warnings = _reset_warnings(inventory)
    data = {
        "version": "10.2",
        "mode": "demo-reset-safety-check",
        "status": "Safe for demo reset" if not warnings else "Needs confirmation",
        "ready": True,
        "approval_phrase": DEMO_RESET_APPROVAL,
        "workspace_inventory": inventory,
        "warnings": warnings,
        "guardrails": _reset_guardrails(),
    }
    data["content"] = _reset_check_markdown(data)
    return data


def v10_2_demo_reset_plan(db: Session) -> dict:
    check = v10_2_demo_reset_safety_check(db)
    data = {
        "version": "10.2",
        "mode": "hardened-demo-reset-plan",
        "status": "Ready",
        "ready": True,
        "approval_phrase": DEMO_RESET_APPROVAL,
        "precheck_status": check["status"],
        "plan_steps": _reset_plan_steps(),
        "rollback_note": "Demo reset rebuilds local demo data. Export evidence before resetting if you need records.",
    }
    data["content"] = _reset_plan_markdown(data)
    return data


def v10_2_operator_first_run_package(db: Session) -> dict:
    wizard = v10_2_first_run_wizard(db)
    reset_check = v10_2_demo_reset_safety_check(db)
    reset_plan = v10_2_demo_reset_plan(db)
    data = {
        "version": "10.2",
        "mode": "operator-first-run-package",
        "status": "Ready",
        "ready": True,
        "included_exports": [wizard["mode"], reset_check["mode"], reset_plan["mode"]],
    }
    data["content"] = "# v10.2 Operator First-run Package\n\n" + "\n\n".join(
        [wizard["content"], reset_check["content"], reset_plan["content"]]
    )
    return data


def _workspace_inventory(db: Session) -> dict:
    return {
        "projects": _count(db, Project.id),
        "releases": _count(db, Release.id),
        "requirements": _count(db, Requirement.id),
        "work_items": _count(db, WorkItem.id),
        "users": _count(db, User.id),
        "has_demo_project": bool(db.scalars(select(Project).where(Project.name == "Payroll System")).first()),
    }


def _count(db: Session, column) -> int:
    return int(db.scalar(select(func.count(column))) or 0)


def _wizard_steps(inventory: dict) -> list[dict]:
    has_data = inventory["projects"] > 0
    return [
        _step(
            1,
            "Confirm local mode",
            "Open the app locally and verify you are not operating against production.",
            "Ready",
        ),
        _step(2, "Review reset safety", "Open Demo Reset Safety before rebuilding sample data.", "Ready"),
        _step(3, "Create or reset demo data", "Use demo reset only after reviewing the approval phrase.", "Ready"),
        _step(
            4,
            "Select project/release",
            "Choose the demo project and release from the workspace selector.",
            "Ready" if has_data else "Blocked",
        ),
        _step(
            5,
            "Run governance tour",
            "Open v10.1 Quickstart, Evidence Manifest, Verified Gate, and Final Bundle.",
            "Ready" if has_data else "Blocked",
        ),
        _step(6, "Export first-run package", "Export this wizard package for operator handoff.", "Ready"),
    ]


def _step(number: int, name: str, action: str, status: str) -> dict:
    return {"step": number, "name": name, "action": action, "status": status}


def _next_safe_action(steps: list[dict]) -> str:
    for step in steps:
        if step["status"] == "Blocked":
            return f"Resolve: {step['name']}"
    return "Open v10.2 first-run package or continue with the v10.1 quickstart."


def _safety_notes() -> list[str]:
    return [
        "Use demo reset for local demo/test databases only.",
        "Export evidence before resetting if the current data matters.",
        "Production migration still requires the v8.5 approval phrase and is unrelated to demo reset.",
        "No private key is requested by first-run flows.",
    ]


def _reset_warnings(inventory: dict) -> list[str]:
    warnings: list[str] = []
    if inventory["projects"] > 1:
        warnings.append("Multiple projects exist; demo reset would replace more than a blank demo workspace.")
    if inventory["work_items"] > 5 or inventory["requirements"] > 3:
        warnings.append("Workspace has non-trivial requirement/work item data; export evidence first.")
    if inventory["users"] > 1:
        warnings.append("Multiple users exist; confirm this is not shared production data.")
    return warnings


def _reset_guardrails() -> list[str]:
    return [
        "Show workspace inventory before reset.",
        "Require an explicit demo-reset approval phrase in v10.2 guided flows.",
        "Keep the legacy /api/demo/reset endpoint for tests and old demos, but document the safer guided path.",
        "Never combine demo reset with production migration commands.",
    ]


def _reset_plan_steps() -> list[str]:
    return [
        "Open Demo Reset Safety and review current workspace inventory.",
        "Export evidence or quickstart package if existing data matters.",
        f"Type approval phrase: {DEMO_RESET_APPROVAL}",
        "Call the demo reset endpoint only after confirmation.",
        "Re-open First-run Wizard and verify demo project, release, requirement, and work items exist.",
    ]


def _wizard_markdown(data: dict) -> str:
    lines = ["# v10.2 Guided First-run Wizard", "", f"Status: {data['status']}", "", "## Workspace inventory"]
    lines.extend(f"- **{key}**: {value}" for key, value in data["workspace_inventory"].items())
    lines.extend(["", "## Steps"])
    lines.extend(f"{row['step']}. **{row['name']}** [{row['status']}] — {row['action']}" for row in data["steps"])
    lines.extend(["", "## Next safe action", data["next_safe_action"], "", "## Safety notes"])
    lines.extend(f"- {item}" for item in data["safety_notes"])
    return "\n".join(lines).strip() + "\n"


def _reset_check_markdown(data: dict) -> str:
    lines = ["# v10.2 Demo Reset Safety Check", "", f"Status: {data['status']}", "", "## Workspace inventory"]
    lines.extend(f"- **{key}**: {value}" for key, value in data["workspace_inventory"].items())
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {item}" for item in (data["warnings"] or ["No reset warnings detected."]))
    lines.extend(["", "## Approval phrase", f"`{data['approval_phrase']}`", "", "## Guardrails"])
    lines.extend(f"- {item}" for item in data["guardrails"])
    return "\n".join(lines).strip() + "\n"


def _reset_plan_markdown(data: dict) -> str:
    lines = ["# v10.2 Hardened Demo Reset Plan", "", f"Status: {data['status']}", "", "## Plan"]
    lines.extend(f"{index}. {item}" for index, item in enumerate(data["plan_steps"], start=1))
    lines.extend(["", "## Rollback note", data["rollback_note"]])
    return "\n".join(lines).strip() + "\n"
