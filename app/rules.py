CRITICAL_PRIORITIES = {"Critical", "High"}
OPEN_STATUSES = {"Open", "In Progress", "Blocked"}
BLOCKING_BUG_SEVERITIES = {"Critical", "Blocker", "High"}


def risk_rules(requirement: dict, work_items: list[dict]) -> list[dict]:
    risks = []
    tasks = [item for item in work_items if item["kind"] == "task"]
    tests = [item for item in work_items if item["kind"] == "test"]
    bugs = [item for item in work_items if item["kind"] == "bug"]
    if requirement["priority"] in CRITICAL_PRIORITIES and not tests:
        risks.append(_risk("critical_requirement_without_test", "Critical requirement has no test coverage.", "High", True))
    if not tasks:
        risks.append(_risk("requirement_without_task", "Requirement has no implementation task.", "Medium", False))
    open_blocking_bugs = [bug for bug in bugs if bug["status"] in OPEN_STATUSES and bug["severity"] in BLOCKING_BUG_SEVERITIES]
    if open_blocking_bugs:
        risks.append(_risk("open_blocking_bug", "Requirement has open high or critical bug.", "Critical", True))
    return risks


def readiness_score(risks: list[dict]) -> int:
    score = 100
    for risk in risks:
        score -= {"Critical": 30, "High": 20, "Medium": 10}.get(risk["severity"], 5)
    return max(score, 0)


def quality_gate(score: int, blocking_risks: int) -> bool:
    return score >= 80 and blocking_risks == 0


def recommendations(risks: list[dict]) -> list[str]:
    if not risks:
        return ["Release looks safe based on current rules."]
    output = []
    for risk in risks:
        if risk["rule_id"] == "critical_requirement_without_test":
            output.append("Add tests for critical/high requirements.")
        if risk["rule_id"] == "requirement_without_task":
            output.append("Link implementation tasks to all requirements.")
        if risk["rule_id"] == "open_blocking_bug":
            output.append("Fix or close high/critical bugs before release.")
    return sorted(set(output))


def _risk(rule_id: str, message: str, severity: str, blocking: bool) -> dict:
    return {"rule_id": rule_id, "title": rule_id.replace("_", " ").title(), "message": message, "severity": severity, "blocking": blocking}
