from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.auth_mode import current_auth_mode, security_checklist


def main() -> int:
    checks = security_checklist()
    print(f"Auth mode: {current_auth_mode()}")
    for item in checks:
        status = "PASS" if item["passed"] else ("BLOCK" if item["blocking"] else "WARN")
        print(f"{status}: {item['key']} - {item['message']}")
    return 0 if all(item["passed"] or not item["blocking"] for item in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
