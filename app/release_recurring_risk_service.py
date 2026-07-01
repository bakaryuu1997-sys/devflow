from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ReleaseSignOff
from app.release_snapshot_service import snapshot_from_signoff

SEVERITY_RANK = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}


def recurring_risk_trends(db: Session, project_id: int, limit: int = 5) -> dict:
    signoffs = _project_signoffs(db, project_id, limit)
    if not signoffs:
        return _empty(project_id)
    snapshots = [snapshot_from_signoff(row) for row in signoffs]
    snapshots_oldest_first = list(reversed(list(zip(signoffs, snapshots, strict=True))))
    occurrences = _risk_occurrences(snapshots_oldest_first)
    recurring = [row for row in occurrences.values() if row["snapshot_occurrences"] >= 2]
    recurring.sort(key=lambda row: (row["blocking_occurrences"], row["snapshot_occurrences"], _rank(row["latest_severity"])), reverse=True)
    data = {
        "project_id": project_id,
        "snapshot_count": len(signoffs),
        "structured_snapshot_count": sum(1 for row in signoffs if bool(row.snapshot_json)),
        "can_analyze": len(signoffs) >= 2,
        "recurring_risks": recurring,
        "latest_snapshot_risks": _latest_snapshot_risks(signoffs[0], snapshots[0]),
        "action_hints": _action_hints(recurring),
    }
    data["content"] = recurring_risk_markdown(data)
    return data


def recurring_risk_markdown(data: dict) -> str:
    if not data.get("can_analyze"):
        return "# Recurring Risk Trends\n\nCreate at least two structured sign-off snapshots to analyze recurring risks.\n"
    lines = [
        "# Recurring Risk Trends",
        "",
        f"Snapshots analyzed: {data['snapshot_count']}",
        f"Recurring risk patterns: {len(data.get('recurring_risks', []))}",
        "",
        "## Prevention hints",
    ]
    lines.extend([f"- {hint}" for hint in data.get("action_hints", [])] or ["- No recurring risk pattern found yet."])
    lines.extend(["", "## Recurring risks"])
    if not data.get("recurring_risks"):
        lines.append("- None")
    for row in data.get("recurring_risks", []):
        lines.append(
            f"- {row['rule_id']} · {row['title']} | snapshots {row['snapshot_occurrences']} | "
            f"blocking {row['blocking_occurrences']} | latest {row['latest_severity']} | "
            f"requirements: {', '.join(row['affected_requirements'])}"
        )
    return "\n".join(lines).strip() + "\n"


def _project_signoffs(db: Session, project_id: int, limit: int) -> list[ReleaseSignOff]:
    rows = db.scalars(
        select(ReleaseSignOff).where(ReleaseSignOff.project_id == project_id).order_by(ReleaseSignOff.created_at.desc())
    ).all()
    return list(rows)[: max(2, min(limit, 20))]


def _risk_occurrences(signoff_snapshots: list[tuple[ReleaseSignOff, dict]]) -> dict[str, dict]:
    rows: dict[str, dict] = {}
    seen_per_snapshot: dict[str, set[str]] = defaultdict(set)
    for signoff, snapshot in signoff_snapshots:
        label = f"{snapshot.get('release', {}).get('version', signoff.release_version)}#{signoff.id}"
        for req in snapshot.get("requirements", []) or []:
            for risk in req.get("risk_events", []) or []:
                rule_id = risk.get("rule_id") or "unknown"
                row = rows.setdefault(rule_id, _new_row(rule_id, risk))
                if rule_id not in seen_per_snapshot[label]:
                    row["snapshot_occurrences"] += 1
                    row["seen_in_snapshots"].append(label)
                    seen_per_snapshot[label].add(rule_id)
                row["total_events"] += 1
                row["blocking_occurrences"] += 1 if risk.get("blocking") else 0
                row["latest_title"] = risk.get("title", row["title"])
                row["latest_severity"] = _higher(row["latest_severity"], risk.get("severity", "Low"))
                key = req.get("key") or "unknown requirement"
                if key not in row["affected_requirements"]:
                    row["affected_requirements"].append(key)
    return rows


def _new_row(rule_id: str, risk: dict) -> dict:
    return {
        "rule_id": rule_id,
        "title": risk.get("title", "Untitled risk"),
        "latest_title": risk.get("title", "Untitled risk"),
        "latest_severity": risk.get("severity", "Low"),
        "snapshot_occurrences": 0,
        "total_events": 0,
        "blocking_occurrences": 0,
        "affected_requirements": [],
        "seen_in_snapshots": [],
    }


def _latest_snapshot_risks(signoff: ReleaseSignOff, snapshot: dict) -> list[dict]:
    rows = []
    for req in snapshot.get("requirements", []) or []:
        for risk in req.get("risk_events", []) or []:
            rows.append({
                "signoff_id": signoff.id,
                "requirement_key": req.get("key"),
                "rule_id": risk.get("rule_id"),
                "title": risk.get("title"),
                "severity": risk.get("severity"),
                "blocking": bool(risk.get("blocking")),
            })
    return rows


def _action_hints(rows: list[dict]) -> list[str]:
    hints = []
    for row in rows[:5]:
        if row["blocking_occurrences"]:
            hints.append(f"Prevent repeated blocking risk '{row['rule_id']}' before next sign-off.")
        else:
            hints.append(f"Track recurring risk '{row['rule_id']}' as a prevention checklist item.")
    return hints or ["No recurring risk pattern detected across the selected snapshots."]


def _empty(project_id: int) -> dict:
    return {
        "project_id": project_id,
        "snapshot_count": 0,
        "structured_snapshot_count": 0,
        "can_analyze": False,
        "recurring_risks": [],
        "latest_snapshot_risks": [],
        "action_hints": ["Create release sign-off snapshots before analyzing recurring risk trends."],
        "content": "# Recurring Risk Trends\n\nNo release sign-off snapshots exist yet.\n",
    }


def _rank(severity: str) -> int:
    return SEVERITY_RANK.get(severity, 0)


def _higher(left: str, right: str) -> str:
    return right if _rank(right) > _rank(left) else left
