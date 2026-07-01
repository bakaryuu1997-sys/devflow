from __future__ import annotations

from sqlalchemy.orm import Session

from app.release_scenario_service import release_readiness_scenarios, scope_decision_audit_trail


def release_plan_recommendation(db: Session, project_id: int, target_days: int = 14) -> dict:
    scenarios = release_readiness_scenarios(db, project_id, target_days)
    ranked = sorted(scenarios["scenarios"], key=_rank_key, reverse=True)
    recommended = ranked[0] if ranked else {}
    baseline = scenarios["scenarios"][0] if scenarios["scenarios"] else {}
    actions = _actions(recommended, baseline)
    data = {
        "project_id": project_id,
        "project_name": scenarios["project_name"],
        "target_days": scenarios["target_days"],
        "recommended_plan": recommended,
        "baseline_status": baseline.get("status", "Unknown"),
        "baseline_score": baseline.get("readiness_score", 0),
        "expected_score_gain": recommended.get("readiness_score", 0) - baseline.get("readiness_score", 0),
        "decision_audit_count": scope_decision_audit_trail(db, project_id)["audit_count"],
        "ranked_scenarios": ranked,
        "action_hints": actions,
    }
    data["content"] = _markdown(data)
    return data


def _rank_key(row: dict) -> tuple[int, int, int]:
    status_bonus = {"Ready Candidate": 30, "Needs Scope Decision": 10, "At Risk": 0}.get(row.get("status"), 0)
    return (
        row.get("readiness_score", 0) + status_bonus,
        -row.get("overdue_items", 0),
        -row.get("unscheduled_items", 0),
    )


def _actions(recommended: dict, baseline: dict) -> list[str]:
    if not recommended:
        return ["Create prevention items before release plan recommendation."]
    actions = [
        f"Recommended plan: {recommended['name']} ({recommended['status']}, score {recommended['readiness_score']}/100)."
    ]
    if recommended.get("scope_adjustment", 0) > 0:
        actions.append("Record explicit scope decisions for items moved out by the recommended scenario.")
    if baseline.get("overdue_items", 0):
        actions.append("Resolve overdue prevention items first; they carry the strongest readiness penalty.")
    if baseline.get("unscheduled_items", 0):
        actions.append("Assign due dates or defer unscheduled prevention items before final planning.")
    if recommended.get("name") == "Baseline":
        actions.append("Keep current scope and continue execution tracking.")
    return actions


def _markdown(data: dict) -> str:
    plan = data["recommended_plan"] or {}
    lines = [
        "# Release Plan Recommendation",
        "",
        f"Project: {data['project_name']} (#{data['project_id']})",
        f"Target window: {data['target_days']} day(s)",
        f"Recommended plan: {plan.get('name', 'None')}",
        f"Expected score gain: {data['expected_score_gain']}",
        "",
        "## Action hints",
    ]
    lines.extend(f"- {hint}" for hint in data["action_hints"])
    lines.extend(["", "## Ranked scenarios"])
    for row in data["ranked_scenarios"]:
        lines.append(
            f"- {row['name']}: {row['status']} · score {row['readiness_score']} · scope adjustment {row['scope_adjustment']}"
        )
    return "\n".join(lines).strip() + "\n"
