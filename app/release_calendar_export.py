from __future__ import annotations


def prevention_calendar_markdown(data: dict) -> str:
    lines = [
        f"# Prevention Calendar View - {data['project_name']}",
        "",
        f"Today: {data['today']}",
        f"Scheduled items: {data['scheduled_items']}",
        f"Unscheduled items: {data['unscheduled_items']}",
        f"Overdue items: {data['overdue_items']}",
        "",
        "## Calendar Entries",
    ]
    if not data["calendar"]:
        lines.append("- No scheduled prevention item yet.")
    for day in data["calendar"]:
        lines.append(f"- {day['date']} ({day['bucket']}): {day['count']} item(s)")
        for item in day["items"]:
            lines.append(f"  - #{item['id']} {item['title']} [{item['status']}] owner: {item['owner'] or 'Unassigned'}")
    lines.extend(["", "## Unscheduled"])
    if not data["unscheduled"]:
        lines.append("- No unscheduled prevention item.")
    for item in data["unscheduled"]:
        lines.append(f"- #{item['id']} {item['title']} [{item['status']}] owner: {item['owner'] or 'Unassigned'}")
    lines.extend(["", "## Action Hints"])
    lines.extend(f"- {hint}" for hint in data["action_hints"])
    return "\n".join(lines)


def release_readiness_timeline_markdown(data: dict) -> str:
    lines = [
        f"# Release Readiness Timeline - {data['project_name']}",
        "",
        f"Today: {data['today']}",
        f"Overall status: {data['overall_status']}",
        f"Open prevention items: {data['open_items']}",
        "",
        "## Timeline Checkpoints",
    ]
    for row in data["checkpoints"]:
        lines.extend([
            f"### {row['label']} - {row['date']}",
            f"- Status: {row['status']}",
            f"- Readiness score: {row['readiness_score']}",
            f"- Remaining open after planned due dates: {row['remaining_open_items']}",
            f"- Overdue by checkpoint: {row['overdue_by_checkpoint']}",
            f"- Unscheduled open items: {row['unscheduled_open_items']}",
        ])
    lines.extend(["", "## Action Hints"])
    lines.extend(f"- {hint}" for hint in data["action_hints"])
    return "\n".join(lines)
