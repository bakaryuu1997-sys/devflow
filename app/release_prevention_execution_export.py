from __future__ import annotations


def prevention_execution_board_markdown(data: dict) -> str:
    lines = [
        "# Prevention Execution Board",
        "",
        f"Project: {data['project_name']} (#{data['project_id']})",
        "",
        "## Summary",
        f"- Open items: {data['open_items']}",
        f"- Planned items: {data['planned_items']}",
        f"- Due soon items: {data['due_soon_items']}",
        f"- Overdue items: {data['overdue_items']}",
        f"- Escalated items: {data['escalated_items']}",
        f"- Done items: {data['done_items']}",
        "",
        "## Action hints",
    ]
    lines.extend([f"- {hint}" for hint in data.get("action_hints", [])])
    lines.extend(["", "## Board lanes"])
    for lane_name, rows in data.get("lanes", {}).items():
        lines.append(f"### {lane_name}")
        if not rows:
            lines.append("- No items.")
        for row in rows:
            lines.append(
                f"- #{row['id']} {row['title']} | owner={row['owner'] or 'Unassigned'} | "
                f"due={row['due_date'] or 'No due date'} | status={row['status']}"
            )
    return "\n".join(lines).strip() + "\n"


def overdue_risk_escalations_markdown(data: dict) -> str:
    lines = [
        "# Overdue Risk Escalations",
        "",
        f"Project: {data['project_name']} (#{data['project_id']})",
        f"Overdue items: {data['overdue_items']}",
        f"Escalated items: {data['escalated_items']}",
        "",
        "## Escalations",
    ]
    if not data.get("escalations"):
        lines.append("- No overdue or escalated prevention item right now.")
    for item in data.get("escalations", []):
        lines.append(
            f"- #{item['id']} {item['title']} — {item['level']} — {item['message']} "
            f"Owner: {item['owner'] or 'Unassigned'}; due: {item['due_date'] or 'No due date'}."
        )
    lines.extend(["", "## Action hints"])
    lines.extend([f"- {hint}" for hint in data.get("action_hints", [])])
    return "\n".join(lines).strip() + "\n"
