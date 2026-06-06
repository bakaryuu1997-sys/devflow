from __future__ import annotations

from collections import Counter

DONE_STATUSES = {"Done", "Closed", "Prevented"}


def generated_prevention_items(retrospectives: list, risk_dashboard: dict) -> list[dict]:
    items: list[dict] = []
    for note in retrospectives[:5]:
        for action in split_actions(note.action_items):
            items.append({"source": f"retrospective#{note.id}", "title": short_title(action), "prevention_action": action})
        if note.what_to_improve.strip():
            items.append({
                "source": f"retrospective#{note.id}",
                "title": "Prevent repeated improvement gap",
                "prevention_action": note.what_to_improve.strip(),
            })
    for signal in recurring_risk_signals(risk_dashboard):
        items.append({"source": "recurring-risk", "title": signal["title"], "prevention_action": signal["prevention_action"]})
    if not items:
        items.append({
            "source": "release-review",
            "title": "Keep pre-signoff review ritual",
            "prevention_action": "Run risk dashboard, done gates, and final sign-off snapshot before every release.",
        })
    return dedupe(items)[:10]


def recurring_risk_signals(risk_dashboard: dict) -> list[dict]:
    risks = []
    for row in risk_dashboard.get("requirements", []):
        risks.extend(row.get("risks", []))
    counts = Counter(risk.get("rule_id", "unknown") for risk in risks)
    signals = []
    for rule_id, count in counts.most_common():
        blocking = sum(1 for risk in risks if risk.get("rule_id") == rule_id and risk.get("blocking"))
        if count < 2 and blocking == 0:
            continue
        signals.append({
            "rule_id": rule_id,
            "count": count,
            "blocking_count": blocking,
            "title": risk_title(rule_id),
            "prevention_action": risk_prevention_action(rule_id),
        })
    return signals


def merge_checklist(generated: list[dict], saved: list[dict]) -> list[dict]:
    merged = [
        {"source": f"saved#{item['id']}", "title": item["title"], "prevention_action": item["prevention_action"]}
        for item in saved
    ]
    merged.extend(generated)
    return dedupe(merged)[:12]


def split_actions(text: str) -> list[str]:
    raw = text.replace(";", "\n").splitlines()
    return [line.strip(" -\t") for line in raw if line.strip(" -\t")][:5]


def short_title(text: str) -> str:
    trimmed = text.strip().rstrip(".")
    return trimmed[:72] + ("…" if len(trimmed) > 72 else "")


def risk_title(rule_id: str) -> str:
    return {
        "critical_requirement_without_test": "Prevent high-priority requirements without test coverage",
        "requirement_without_task": "Prevent requirements without implementation tasks",
        "open_blocking_bug": "Prevent open blocking bugs at release review",
    }.get(rule_id, f"Prevent recurring risk: {rule_id}")


def risk_prevention_action(rule_id: str) -> str:
    return {
        "critical_requirement_without_test": "Add a test placeholder when a High/Critical requirement is created, then convert it before review.",
        "requirement_without_task": "Create or link an implementation task during requirement intake, not during final release review.",
        "open_blocking_bug": "Review open High/Critical bugs before sign-off and require owner/date before release review.",
    }.get(rule_id, "Add a concrete prevention rule to the next release checklist.")


def dedupe(items: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for item in items:
        key = (item.get("title", "").lower(), item.get("prevention_action", "").lower())
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def signal_lines(signals: list[dict]) -> list[str]:
    if not signals:
        return ["- No repeated active risk pattern detected."]
    return [
        f"- {s['rule_id']}: {s['count']} occurrence(s), {s['blocking_count']} blocking — {s['prevention_action']}"
        for s in signals
    ]
