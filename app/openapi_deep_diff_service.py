import json


def deep_openapi_diff(before_raw: str, after_raw: str) -> list[dict]:
    before = json.loads(before_raw)
    after = json.loads(after_raw)
    findings = []
    before_paths = before.get("paths") or {}
    after_paths = after.get("paths") or {}

    for path, methods in before_paths.items():
        if path not in after_paths:
            findings.append(_finding(path, "*", "High", f"Endpoint removed: {path}", True))
            continue
        for method, spec in methods.items():
            if method not in after_paths[path]:
                findings.append(_finding(path, method, "High", f"Operation removed: {method.upper()} {path}", True))
                continue
            findings.extend(_compare_operation(path, method, spec or {}, after_paths[path][method] or {}))

    for path, methods in after_paths.items():
        if path not in before_paths:
            findings.append(_finding(path, "*", "Low", f"Endpoint added: {path}", False))
    return findings or [_finding("-", "-", "Low", "No deep OpenAPI breaking change detected.", False)]


def _compare_operation(path: str, method: str, before: dict, after: dict) -> list[dict]:
    findings = []
    before_params = _param_names(before)
    after_params = _param_names(after)
    for name in sorted(after_params - before_params):
        if _required_param(after, name):
            findings.append(_finding(path, method, "Medium", f"New required parameter: {name}", True))
    before_responses = set((before.get("responses") or {}).keys())
    after_responses = set((after.get("responses") or {}).keys())
    for code in sorted(before_responses - after_responses):
        findings.append(_finding(path, method, "Medium", f"Response status removed: {code}", False))
    return findings


def _param_names(operation: dict) -> set:
    return {p.get("name") for p in operation.get("parameters", []) if p.get("name")}


def _required_param(operation: dict, name: str) -> bool:
    for param in operation.get("parameters", []):
        if param.get("name") == name:
            return bool(param.get("required"))
    return False


def _finding(path: str, method: str, severity: str, message: str, blocking: bool) -> dict:
    return {"path": path, "method": method, "severity": severity, "message": message, "blocking": blocking}
