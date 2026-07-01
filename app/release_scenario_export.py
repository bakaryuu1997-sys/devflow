from __future__ import annotations


def scenario_planning_markdown(data: dict) -> str:
    lines = [
        "# Release Readiness Scenario Planning",
        "",
        f"Project: {data['project_name']} (#{data['project_id']})",
        f"Target window: {data['target_days']} day(s)",
        "",
        "## Scenarios",
    ]
    for row in data["scenarios"]:
        lines.extend(
            [
                f"### {row['name']}",
                f"- Status: {row['status']}",
                f"- Readiness score: {row['readiness_score']}/100",
                f"- Active scope items: {row['active_scope_items']}",
                f"- Overdue: {row['overdue_items']}",
                f"- Unscheduled: {row['unscheduled_items']}",
                f"- Due within target: {row['due_within_target_items']}",
                f"- Scope adjustment: {row['scope_adjustment']}",
                "",
            ]
        )
    lines.extend(["## Recommended actions"])
    lines.extend([f"- {hint}" for hint in data["action_hints"]])
    return "\n".join(lines).strip() + "\n"


def scope_adjustment_markdown(data: dict) -> str:
    item = data["item"]
    return "\n".join(
        [
            "# Prevention Scope Adjustment",
            "",
            f"Item: #{item['id']} {item['title']}",
            f"Status: {item['status']}",
            f"Owner: {item.get('owner') or 'Unassigned'}",
            f"Due date: {item.get('due_date') or 'No due date'}",
            f"Reason: {data.get('reason') or 'No reason provided'}",
            "",
        ]
    )
