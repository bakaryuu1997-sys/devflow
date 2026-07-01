from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.demo_profiles_data import DEMO_PROFILES, TUTORIAL_STEPS
from app.models_v103 import TutorialProgress
from app.time_utils import utc_now

VALID_STATUSES = {"Open", "In Progress", "Done", "Skipped"}


def v10_3_demo_data_profiles() -> dict:
    data = {
        "version": "10.3",
        "mode": "demo-data-profiles",
        "status": "Ready",
        "ready": True,
        "profiles": DEMO_PROFILES,
        "safety_notes": _profile_safety_notes(),
    }
    data["content"] = _profiles_markdown(data)
    return data


def v10_3_demo_profile_reset_plan(profile_id: str = "core-risk") -> dict:
    profile = _find_profile(profile_id)
    data = {
        "version": "10.3",
        "mode": "demo-profile-reset-plan",
        "status": "Ready" if profile else "Unknown profile",
        "ready": bool(profile),
        "profile": profile,
        "plan_steps": _profile_plan_steps(profile) if profile else [],
        "guardrails": _profile_guardrails(),
    }
    data["content"] = _profile_plan_markdown(data)
    return data


def v10_3_tutorial_progress(db: Session) -> dict:
    records = _progress_map(db)
    steps = [_tutorial_row(step_id, name, action, records.get(step_id)) for step_id, name, action in TUTORIAL_STEPS]
    done = sum(1 for row in steps if row["status"] == "Done")
    percent = int((done / len(steps)) * 100) if steps else 0
    data = {
        "version": "10.3",
        "mode": "tutorial-mode-progress",
        "status": "Complete" if percent == 100 else "In Progress",
        "ready": True,
        "completion_percent": percent,
        "steps": steps,
        "next_step": _next_step(steps),
    }
    data["content"] = _progress_markdown(data)
    return data


def v10_3_update_tutorial_step(
    db: Session, step_id: str, status: str = "Done", operator_name: str = "", notes: str = ""
) -> dict:
    if step_id not in {row[0] for row in TUTORIAL_STEPS}:
        return {"version": "10.3", "mode": "tutorial-step-update", "status": "Unknown step", "ready": False}
    if status not in VALID_STATUSES:
        return {"version": "10.3", "mode": "tutorial-step-update", "status": "Invalid status", "ready": False}
    record = db.scalars(select(TutorialProgress).where(TutorialProgress.step_id == step_id)).first()
    if not record:
        record = TutorialProgress(step_id=step_id)
        db.add(record)
    record.status = status
    record.operator_name = operator_name
    record.notes = notes
    record.updated_at = utc_now()
    db.commit()
    return {
        "version": "10.3",
        "mode": "tutorial-step-update",
        "status": "Saved",
        "ready": True,
        "step_id": step_id,
        "step_status": status,
    }


def v10_3_operator_tutorial_package(db: Session) -> dict:
    profiles = v10_3_demo_data_profiles()
    progress = v10_3_tutorial_progress(db)
    plan = v10_3_demo_profile_reset_plan("core-risk")
    data = {"version": "10.3", "mode": "operator-tutorial-package", "status": "Ready", "ready": True}
    data["content"] = "# v10.3 Operator Tutorial Package\n\n" + "\n\n".join(
        [profiles["content"], plan["content"], progress["content"]]
    )
    return data


def _find_profile(profile_id: str) -> dict | None:
    return next((profile for profile in DEMO_PROFILES if profile["profile_id"] == profile_id), None)


def _progress_map(db: Session) -> dict[str, TutorialProgress]:
    return {row.step_id: row for row in db.scalars(select(TutorialProgress)).all()}


def _tutorial_row(step_id: str, name: str, action: str, record: TutorialProgress | None) -> dict:
    return {
        "step_id": step_id,
        "name": name,
        "action": action,
        "status": record.status if record else "Open",
        "notes": record.notes if record else "",
    }


def _next_step(steps: list[dict]) -> str:
    for row in steps:
        if row["status"] != "Done":
            return row["name"]
    return "Tutorial complete. Export the operator tutorial package."


def _profile_safety_notes() -> list[str]:
    return [
        "Profiles are deterministic demo presets, not production migrations.",
        "Use v10.2 reset safety before rebuilding demo data.",
        "Private keys are never included in demo profiles.",
    ]


def _profile_guardrails() -> list[str]:
    return [
        "Preview selected profile before reset.",
        "Keep old /api/demo/reset backward compatible.",
        "Do not mix demo profile reset with production DB migration.",
    ]


def _profile_plan_steps(profile: dict | None) -> list[str]:
    if not profile:
        return []
    return [
        f"Select profile: {profile['name']}.",
        "Run v10.2 Demo Reset Safety.",
        "Reset or seed local demo data only after confirmation.",
        "Open tutorial progress and mark the profile step complete.",
    ]


def _profiles_markdown(data: dict) -> str:
    lines = ["# v10.3 Demo Data Profiles", "", f"Status: {data['status']}", "", "## Profiles"]
    lines.extend(
        f"- **{p['name']}** (`{p['profile_id']}`): {p['description']} Risk: {p['risk_level']}."
        for p in data["profiles"]
    )
    lines.extend(["", "## Safety notes", *[f"- {item}" for item in data["safety_notes"]]])
    return "\n".join(lines).strip() + "\n"


def _profile_plan_markdown(data: dict) -> str:
    title = data["profile"]["name"] if data["profile"] else "Unknown profile"
    lines = ["# v10.3 Demo Profile Reset Plan", "", f"Profile: {title}", f"Status: {data['status']}", "", "## Plan"]
    lines.extend(
        f"{i}. {item}" for i, item in enumerate(data["plan_steps"] or ["Choose a valid profile first."], start=1)
    )
    lines.extend(["", "## Guardrails", *[f"- {item}" for item in data["guardrails"]]])
    return "\n".join(lines).strip() + "\n"


def _progress_markdown(data: dict) -> str:
    lines = ["# v10.3 Tutorial Mode Progress", "", f"Completion: {data['completion_percent']}%", "", "## Steps"]
    lines.extend(f"- [{row['status']}] **{row['name']}** — {row['action']}" for row in data["steps"])
    lines.extend(["", "## Next step", data["next_step"]])
    return "\n".join(lines).strip() + "\n"
