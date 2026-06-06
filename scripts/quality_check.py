from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKED_EXTENSIONS = {".py", ".md", ".js", ".css", ".html", ".yml", ".yaml", ".ini", ".sh", ".txt"}
MAX_LINES = 200
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-proj-[A-Za-z0-9_-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]
IGNORED_DIRS = {"__pycache__", ".pytest_cache", ".git", "node_modules", ".venv", "venv"}


def main() -> int:
    failures: list[str] = []
    failures.extend(check_file_sizes())
    failures.extend(check_secrets())
    failures.extend(check_required_files())
    if failures:
        print("QUALITY CHECK FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("QUALITY CHECK PASSED")
    return 0


def check_file_sizes() -> list[str]:
    failures = []
    for path in iter_files():
        line_count = len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
        if line_count > MAX_LINES:
            failures.append(f"{path.relative_to(ROOT)} has {line_count} lines")
    return failures


def check_secrets() -> list[str]:
    failures = []
    for path in iter_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                failures.append(f"possible secret in {path.relative_to(ROOT)}")
    return failures


def check_required_files() -> list[str]:
    required = ["requirements.txt", ".env.example", "rules.md", "goal.md"]
    return [f"missing required file: {name}" for name in required if not (ROOT / name).exists()]


def iter_files():
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in CHECKED_EXTENSIONS:
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        yield path


if __name__ == "__main__":
    raise SystemExit(main())
