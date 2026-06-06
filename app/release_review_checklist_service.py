from __future__ import annotations

from datetime import datetime

from app.release_risk_dashboard_service import release_risk_dashboard
from app.time_utils import utc_now


def release_review_checklist(db, project_id: int) -> dict:
    dashboard = release_risk_dashboard(db, project_id)
    generated_at = utc_now()
    content = _markdown(dashboard, generated_at)
    return {
        "project_id": project_id,
        "generated_at": generated_at.isoformat(),
        "release_status": dashboard["release_status"],
        "blocking_risks": dashboard["blocking_risks"],
        "total_risks": dashboard["total_risks"],
        "content": content,
    }


def _markdown(dashboard: dict, generated_at: datetime) -> str:
    lines = [
        "# Release Review Checklist",
        "",
        f"Generated at: {generated_at.isoformat()}",
        f"Release status: {dashboard['release_status']}",
        f"Total risks: {dashboard['total_risks']}",
        f"Blocking risks: {dashboard['blocking_risks']}",
        "",
        "## Top actions",
    ]
    for action in dashboard.get("top_actions", []):
        lines.append(f"- [ ] {action}")
    lines.extend(["", "## Requirement review"])
    for row in dashboard.get("requirements", []):
        lines.extend(_requirement_lines(row))
    if not dashboard.get("requirements"):
        lines.append("- [x] No active requirements need review.")
    return "\n".join(lines).strip() + "\n"


def _requirement_lines(row: dict) -> list[str]:
    header = f"### {row['requirement_key']} — {row['requirement_title']}"
    lines = [
        "",
        header,
        f"- Priority: {row['priority']}",
        f"- Status: {row['status']}",
        f"- Score: {row['score']}",
        f"- Risks: {row['risk_count']} total, {row['blocking_risks']} blocking",
    ]
    if row.get("fix_hints"):
        lines.append("- Fix checklist:")
        for hint in row["fix_hints"]:
            lines.append(f"  - [ ] {hint}")
    else:
        lines.append("- [x] No active fix hint for this requirement.")
    for risk in row.get("risks", []):
        lines.append(f"- Risk: {risk['severity']} — {risk['title']}")
    return lines
