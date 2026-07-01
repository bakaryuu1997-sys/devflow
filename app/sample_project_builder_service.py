from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project, Release, Requirement, TraceLink, WorkItem
from app.sample_project_builder_data import BUILDER_STEPS, SAMPLE_PROFILE_SEEDS
from app.tutorial_mode_service import v10_3_tutorial_progress, v10_3_update_tutorial_step


def v10_4_sample_project_builder(profile_id: str = "core-risk") -> dict:
    seed = SAMPLE_PROFILE_SEEDS.get(profile_id)
    data = {
        "version": "10.4",
        "mode": "guided-sample-project-builder",
        "status": "Ready" if seed else "Unknown profile",
        "ready": bool(seed),
        "profile_id": profile_id,
        "sample_preview": _preview(seed) if seed else {},
        "builder_steps": BUILDER_STEPS,
        "guardrails": _guardrails(),
    }
    data["content"] = _builder_markdown(data)
    return data


def v10_4_build_sample_project(db: Session, profile_id: str = "core-risk", operator_name: str = "") -> dict:
    seed = SAMPLE_PROFILE_SEEDS.get(profile_id)
    if not seed:
        return _error(profile_id)
    project = _existing_project(db, seed["project"][0]) or _create_project(db, seed)
    counts = _seed_project_children(db, project, seed)
    v10_3_update_tutorial_step(db, "sample-builder", "Done", operator_name, f"Built {profile_id}")
    badge = v10_4_tutorial_completion_badge(db)
    data = {
        "version": "10.4",
        "mode": "guided-sample-project-build-result",
        "status": "Built",
        "ready": True,
        "profile_id": profile_id,
        "project_id": project.id,
        "created_or_reused": counts,
        "completion_badge": badge["badge"],
    }
    data["content"] = _build_markdown(data)
    return data


def v10_4_tutorial_completion_badge(db: Session) -> dict:
    progress = v10_3_tutorial_progress(db)
    complete = progress["completion_percent"] == 100
    badge = {
        "label": "Tutorial Complete" if complete else "Tutorial In Progress",
        "level": "gold" if complete else "blue",
        "earned": complete,
        "completion_percent": progress["completion_percent"],
        "next_step": progress["next_step"],
    }
    data = {
        "version": "10.4",
        "mode": "tutorial-completion-badge",
        "status": badge["label"],
        "ready": True,
        "badge": badge,
    }
    data["content"] = _badge_markdown(data)
    return data


def v10_4_operator_sample_builder_package(db: Session) -> dict:
    builder = v10_4_sample_project_builder("core-risk")
    badge = v10_4_tutorial_completion_badge(db)
    data = {"version": "10.4", "mode": "operator-sample-builder-package", "status": "Ready", "ready": True}
    data["content"] = "# v10.4 Operator Sample Builder Package\n\n" + "\n\n".join(
        [builder["content"], badge["content"]]
    )
    return data


def _existing_project(db: Session, name: str) -> Project | None:
    return db.scalars(select(Project).where(Project.name == name)).first()


def _create_project(db: Session, seed: dict) -> Project:
    name, description = seed["project"]
    project = Project(name=name, description=description)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def _seed_project_children(db: Session, project: Project, seed: dict) -> dict:
    reqs = _seed_requirements(db, project, seed["requirements"])
    work_items = _seed_work_items(db, project, reqs, seed["work_items"])
    links = _seed_links(db, project, seed["links"])
    release = _seed_release(db, project, seed["release"])
    db.commit()
    return {"requirements": len(reqs), "work_items": work_items, "trace_links": links, "release_id": release.id}


def _seed_requirements(db: Session, project: Project, rows: list[tuple]) -> dict[str, Requirement]:
    reqs: dict[str, Requirement] = {}
    for key, title, priority, status in rows:
        req = db.scalars(
            select(Requirement).where(Requirement.project_id == project.id, Requirement.key == key)
        ).first()
        if not req:
            req = Requirement(project_id=project.id, key=key, title=title, priority=priority, status=status)
            db.add(req)
            db.flush()
        reqs[key] = req
    return reqs


def _seed_work_items(db: Session, project: Project, reqs: dict[str, Requirement], rows: list[tuple]) -> int:
    count = 0
    for kind, title, status, severity, req_key in rows:
        exists = db.scalars(select(WorkItem).where(WorkItem.project_id == project.id, WorkItem.title == title)).first()
        if not exists:
            db.add(
                WorkItem(
                    project_id=project.id,
                    requirement_id=reqs[req_key].id,
                    kind=kind,
                    title=title,
                    status=status,
                    severity=severity,
                )
            )
        count += 1
    return count


def _seed_links(db: Session, project: Project, rows: list[tuple]) -> int:
    for link_type, target, title, status, req_key in rows:
        exists = db.scalars(
            select(TraceLink).where(TraceLink.project_id == project.id, TraceLink.target_key == target)
        ).first()
        if not exists:
            db.add(
                TraceLink(
                    project_id=project.id,
                    requirement_key=req_key,
                    link_type=link_type,
                    target_key=target,
                    title=title,
                    status=status,
                )
            )
    return len(rows)


def _seed_release(db: Session, project: Project, version: str) -> Release:
    release = db.scalars(select(Release).where(Release.project_id == project.id, Release.version == version)).first()
    if not release:
        release = Release(project_id=project.id, version=version)
        db.add(release)
        db.flush()
    return release


def _preview(seed: dict) -> dict:
    return {
        "project": seed["project"][0],
        "release": seed["release"],
        "requirements": len(seed["requirements"]),
        "work_items": len(seed["work_items"]),
        "trace_links": len(seed["links"]),
    }


def _guardrails() -> list[str]:
    return [
        "Builder creates/reuses a named sample project; it does not drop tables.",
        "Legacy /api/demo/reset remains unchanged.",
        "Seed data is deterministic per profile.",
    ]


def _error(profile_id: str) -> dict:
    return {
        "version": "10.4",
        "mode": "guided-sample-project-build-result",
        "status": "Unknown profile",
        "ready": False,
        "profile_id": profile_id,
    }


def _builder_markdown(data: dict) -> str:
    lines = ["# v10.4 Guided Sample Project Builder", "", f"Status: {data['status']}", "", "## Preview"]
    lines.extend(f"- **{k}**: {v}" for k, v in data["sample_preview"].items())
    lines.extend(
        ["", "## Steps", *[f"{i}. {step}" for i, step in enumerate(data["builder_steps"], 1)], "", "## Guardrails"]
    )
    lines.extend(f"- {item}" for item in data["guardrails"])
    return "\n".join(lines).strip() + "\n"


def _build_markdown(data: dict) -> str:
    return f"# v10.4 Sample Project Build Result\n\nProject ID: {data['project_id']}\nProfile: {data['profile_id']}\nBadge: {data['completion_badge']['label']}\n"


def _badge_markdown(data: dict) -> str:
    badge = data["badge"]
    return f"# v10.4 Tutorial Completion Badge\n\nLabel: {badge['label']}\nCompletion: {badge['completion_percent']}%\nNext step: {badge['next_step']}\n"
