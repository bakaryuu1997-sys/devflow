import json
import re
import xml.etree.ElementTree as ET

SQL_RULES = [
    ("drop_table", r"\bDROP\s+TABLE\b", "Critical", True),
    ("drop_column", r"\bDROP\s+COLUMN\b", "High", True),
    ("truncate_table", r"\bTRUNCATE\s+TABLE\b", "High", True),
    ("alter_type", r"\bALTER\s+TABLE\b.*\bALTER\s+COLUMN\b.*\bTYPE\b", "Medium", False),
]


def analyze_sql_migration(content: str) -> list[dict]:
    findings = []
    for rule_id, pattern, severity, blocking in SQL_RULES:
        if re.search(pattern, content, flags=re.IGNORECASE | re.DOTALL):
            findings.append(_finding("migration", rule_id, severity, blocking, f"SQL matched {rule_id}."))
    findings.extend(_dangerous_delete_findings(content))
    return findings or [_finding("migration", "safe_migration", "Low", False, "No dangerous SQL pattern detected.")]


def analyze_logs(content: str) -> list[dict]:
    rules = [
        ("error_log", r"\bERROR\b", "High", True),
        ("exception_log", r"Exception|Traceback", "High", True),
        ("timeout_log", r"timeout|timed out", "Medium", False),
        ("warning_log", r"\bWARN(ING)?\b", "Low", False),
    ]
    findings = []
    for rule_id, pattern, severity, blocking in rules:
        count = len(re.findall(pattern, content, flags=re.IGNORECASE))
        if count:
            findings.append(_finding("log", rule_id, severity, blocking, f"Found {count} occurrence(s)."))
    return findings or [_finding("log", "clean_log", "Low", False, "No error pattern detected.")]


def analyze_openapi_diff(before_raw: str, after_raw: str) -> list[dict]:
    before = json.loads(before_raw)
    after = json.loads(after_raw)
    before_paths = set((before.get("paths") or {}).keys())
    after_paths = set((after.get("paths") or {}).keys())
    findings = []
    for path in sorted(before_paths - after_paths):
        findings.append(_finding("api", "removed_endpoint", "High", True, f"Endpoint removed: {path}"))
    for path in sorted(after_paths - before_paths):
        findings.append(_finding("api", "added_endpoint", "Low", False, f"Endpoint added: {path}"))
    return findings or [
        _finding("api", "no_breaking_path_change", "Low", False, "No path-level breaking change detected.")
    ]


def analyze_test_report(content: str) -> list[dict]:
    failed = _extract_failed_tests(content)
    if failed:
        return [_finding("test", "failed_tests", "Critical", True, f"Test report has {failed} failed/error test(s).")]
    return [_finding("test", "tests_passed", "Low", False, "No failed tests detected.")]


def _dangerous_delete_findings(content: str) -> list[dict]:
    findings = []
    for statement in _sql_statements(content):
        if re.search(r"\bDELETE\s+FROM\b", statement, flags=re.IGNORECASE) and not re.search(
            r"\bWHERE\b", statement, flags=re.IGNORECASE
        ):
            findings.append(
                _finding("migration", "delete_without_where", "High", True, "DELETE statement has no WHERE clause.")
            )
    return findings


def _sql_statements(content: str) -> list[str]:
    cleaned = re.sub(r"--.*?$", "", content, flags=re.MULTILINE)
    return [part.strip() for part in cleaned.split(";") if part.strip()]


def _extract_failed_tests(content: str) -> int:
    try:
        root = ET.fromstring(content)
        return int(root.attrib.get("failures", "0")) + int(root.attrib.get("errors", "0"))
    except Exception:
        return len(re.findall(r"\bFAIL(ED)?\b|\bERROR\b", content, flags=re.IGNORECASE))


def _finding(guard_type: str, rule_id: str, severity: str, blocking: bool, message: str) -> dict:
    return {
        "guard_type": guard_type,
        "title": rule_id.replace("_", " ").title(),
        "severity": severity,
        "blocking": blocking,
        "message": message,
    }
