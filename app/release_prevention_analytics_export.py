from __future__ import annotations


def prevention_burndown_markdown(data: dict) -> str:
    lines = [
        "# Prevention Burndown Analytics",
        "",
        f"Project: {data['project_name']} (#{data['project_id']})",
        f"Completion rate: {data['completion_rate']}%",
        "",
        "## Summary",
        f"- Total items: {data['total_items']}",
        f"- Open items: {data['open_items']}",
        f"- Done items: {data['done_items']}",
        f"- Overdue items: {data['overdue_items']}",
        f"- Due soon items: {data['due_soon_items']}",
        "",
        "## Burndown projection",
    ]
    for row in data.get("burndown_projection", []):
        lines.append(
            f"- {row['checkpoint']} ({row['date']}): remaining open={row['remaining_open_items']}, planned closed={row['planned_closed_by_checkpoint']}"
        )
    lines.extend(["", "## Action hints"])
    lines.extend([f"- {hint}" for hint in data.get("action_hints", [])])
    return "\n".join(lines).strip() + "\n"


def owner_workload_markdown(data: dict) -> str:
    lines = [
        "# Owner Workload Balance",
        "",
        f"Project: {data['project_name']} (#{data['project_id']})",
        f"Average open items per owner: {data['average_open_items_per_owner']}",
        "",
        "## Owners",
    ]
    if not data.get("owners"):
        lines.append("- No prevention items yet.")
    for row in data.get("owners", []):
        lines.append(
            f"- {row['owner']}: status={row['status']}, open={row['open_items']}, overdue={row['overdue_items']}, "
            f"due_soon={row['due_soon_items']}, score={row['workload_score']}"
        )
    lines.extend(["", "## Action hints"])
    lines.extend([f"- {hint}" for hint in data.get("action_hints", [])])
    return "\n".join(lines).strip() + "\n"
