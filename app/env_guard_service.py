import re

DEFAULT_REQUIRED = ["DATABASE_URL", "JWT_SECRET_KEY"]


def analyze_env(content: str, required_keys: list[str] | None = None) -> list[dict]:
    required = required_keys or DEFAULT_REQUIRED
    parsed = _parse_env(content)
    findings = []

    for key in required:
        if key not in parsed or not parsed.get(key):
            findings.append(_finding(key, "High", f"Missing required env var: {key}", True))

    for key, value in parsed.items():
        upper_key = key.upper()
        if upper_key in {"APP_DEBUG", "DEBUG"} and value.lower() == "true":
            findings.append(_finding(key, "High", "Debug mode enabled.", True))
        if "SECRET" in upper_key and value in {"", "change-me", "changeme", "default", "test-secret"}:
            findings.append(_finding(key, "High", "Weak/default secret detected.", True))
        if re.search(r"(sk-|ghp_|AKIA|password=)", value, re.IGNORECASE):
            findings.append(_finding(key, "Critical", "Possible committed secret value.", True))

    return findings or [_finding("config", "Low", "No dangerous env config detected.", False)]


def _parse_env(content: str) -> dict[str, str]:
    parsed = {}
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        parsed[key.strip()] = value.strip().strip('"').strip("'")
    return parsed


def _finding(key: str, severity: str, message: str, blocking: bool) -> dict:
    return {"key": key, "severity": severity, "message": message, "blocking": blocking}
