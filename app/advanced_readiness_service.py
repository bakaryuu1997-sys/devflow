from app.bug_pattern_service import bug_pattern_dashboard
from app.guard_service import blocking_guard_count
from app.impact_service import list_requirement_changes
from app.traceability_service import traceability_matrix


def advanced_readiness(db, project_id: int) -> dict:
    matrix = traceability_matrix(db, project_id)
    changes = list_requirement_changes(db, project_id)
    bug_rows = bug_pattern_dashboard(db, project_id)
    guard_blockers = blocking_guard_count(db, project_id)

    blockers = []
    warnings = []
    score = 100

    for row in matrix:
        if row["risk"] == "Critical":
            blockers.append(f"{row['requirement_key']} has critical traceability risk.")
            score -= 25
        elif row["risk"] == "High":
            warnings.append(f"{row['requirement_key']} has high traceability risk.")
            score -= 15
        elif row["risk"] == "Medium":
            score -= 8

    if changes:
        warnings.append(f"{len(changes)} requirement change(s) need review.")
        score -= min(20, len(changes) * 5)

    if guard_blockers:
        blockers.append(f"{guard_blockers} blocking guard finding(s) detected.")
        score -= min(35, guard_blockers * 12)

    for item in bug_rows:
        if item["risk"] in {"Critical", "High"}:
            blockers.append(f"Module {item['module']} has {item['risk']} bug pattern risk.")
            score -= 12

    score = max(score, 0)
    return {
        "project_id": project_id,
        "score": score,
        "status": "Safe" if score >= 80 and not blockers else "Not Safe",
        "blockers": blockers,
        "warnings": warnings,
        "recommendations": _recommendations(blockers, warnings),
    }


def _recommendations(blockers: list[str], warnings: list[str]) -> list[str]:
    actions = []
    if blockers:
        actions.append("Resolve blockers before release.")
    if warnings:
        actions.append("Review warnings and rerun impacted tests.")
    if not actions:
        actions.append("Release looks safe based on current project risk rules.")
    return actions
