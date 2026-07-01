from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project, ReleaseSignOff, ScopeDecisionAudit
from app.release_plan_recommendation_service import release_plan_recommendation
from app.release_signoff_service import release_signoff_snapshot

MIGRATION_NOTES = [
    {"area": "ReleaseSignOff.snapshot_json", "action": "Add nullable Text column for structured sign-off snapshots."},
    {
        "area": "ReleaseLearningItem.owner",
        "action": "Add nullable/default-empty String column for prevention item ownership.",
    },
    {
        "area": "ReleaseLearningItem.due_date",
        "action": "Add nullable/default-empty String column storing ISO date text.",
    },
    {"area": "ScopeDecisionAudit", "action": "Create table for prevention scope decision history."},
]


def governance_readiness(db: Session, project_id: int, target_days: int = 14) -> dict:
    project = db.get(Project, project_id)
    snapshot = release_signoff_snapshot(db, project_id)
    recommendation = release_plan_recommendation(db, project_id, target_days)
    signoffs = _signoffs(db, project_id)
    audit_count = _audit_count(db, project_id)
    checks = _checks(snapshot, recommendation, signoffs, audit_count)
    data = {
        "project_id": project_id,
        "project_name": project.name if project else "Unknown project",
        "target_days": recommendation["target_days"],
        "status": _status(checks),
        "score": _score(checks),
        "ready_for_signoff": snapshot["ready_for_signoff"],
        "recommended_plan": recommendation["recommended_plan"],
        "expected_score_gain": recommendation["expected_score_gain"],
        "signoff_count": len(signoffs),
        "scope_audit_count": audit_count,
        "checks": checks,
        "migration_notes": MIGRATION_NOTES,
        "action_hints": _hints(checks, snapshot, recommendation),
    }
    data["content"] = _markdown(data)
    return data


def migration_notes() -> dict:
    data = {"version": "8.0", "notes": MIGRATION_NOTES, "content": _migration_markdown()}
    return data


def _signoffs(db: Session, project_id: int) -> list[ReleaseSignOff]:
    return list(db.scalars(select(ReleaseSignOff).where(ReleaseSignOff.project_id == project_id)).all())


def _audit_count(db: Session, project_id: int) -> int:
    return len(list(db.scalars(select(ScopeDecisionAudit.id).where(ScopeDecisionAudit.project_id == project_id)).all()))


def _checks(snapshot: dict, recommendation: dict, signoffs: list[ReleaseSignOff], audit_count: int) -> list[dict]:
    plan = recommendation.get("recommended_plan") or {}
    return [
        _check("Structured snapshots", True, "Approval records store JSON snapshots and keep Markdown fallback."),
        _check("Migration notes", True, "v8.0 includes explicit migration notes for fields/tables added since v7.0."),
        _check(
            "Scope decision audit", audit_count > 0, "Record at least one real scope decision before an audit review."
        ),
        _check(
            "Release sign-off gate",
            bool(snapshot.get("ready_for_signoff")),
            "All active requirements must pass done gates and have no blocking risks.",
        ),
        _check("Plan recommendation", bool(plan), "Recommendation engine must return a ranked release plan."),
        _check(
            "Approval history", bool(signoffs), "Create at least one approval record for traceable governance history."
        ),
    ]


def _check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": passed, "detail": detail, "state": "PASS" if passed else "WAIT"}


def _score(checks: list[dict]) -> int:
    if not checks:
        return 0
    return round(sum(1 for row in checks if row["passed"]) * 100 / len(checks))


def _status(checks: list[dict]) -> str:
    score = _score(checks)
    if score == 100:
        return "Audit Ready"
    if score >= 70:
        return "Governance Review Needed"
    return "Governance Gaps"


def _hints(checks: list[dict], snapshot: dict, recommendation: dict) -> list[str]:
    hints = [f"Fix: {row['name']} — {row['detail']}" for row in checks if not row["passed"]]
    if snapshot.get("signoff_blockers"):
        hints.extend(snapshot["signoff_blockers"][:3])
    plan = recommendation.get("recommended_plan") or {}
    if plan.get("name"):
        hints.append(f"Use recommended plan '{plan['name']}' before final governance review.")
    return hints or ["Governance workflow is audit-ready. Export approval and migration notes for review."]


def _markdown(data: dict) -> str:
    lines = [
        "# Release Governance Readiness",
        "",
        f"Project: {data['project_name']} (#{data['project_id']})",
        f"Status: {data['status']} ({data['score']}/100)",
        f"Recommended plan: {data['recommended_plan'].get('name', 'None')}",
        "",
        "## Governance checks",
    ]
    lines.extend(f"- [{'x' if row['passed'] else ' '}] {row['name']}: {row['detail']}" for row in data["checks"])
    lines.extend(["", "## Action hints"])
    lines.extend(f"- {hint}" for hint in data["action_hints"])
    lines.extend(["", "## Migration notes"])
    lines.extend(f"- {row['area']}: {row['action']}" for row in data["migration_notes"])
    return "\n".join(lines).strip() + "\n"


def _migration_markdown() -> str:
    lines = [
        "# v8.0 Migration Notes",
        "",
        "Use these notes when upgrading an existing SQLite database outside demo/test mode.",
        "",
    ]
    lines.extend(f"- **{row['area']}** — {row['action']}" for row in MIGRATION_NOTES)
    lines.extend(
        ["", "Recommended path: back up the database, add nullable/default-safe columns first, then run smoke tests."]
    )
    return "\n".join(lines).strip() + "\n"
