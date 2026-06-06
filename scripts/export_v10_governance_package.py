from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import SessionLocal
from app.stable_milestone_service import v10_stable_milestone_report


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("V10_GOVERNANCE_PACKAGE.md")
    db = SessionLocal()
    try:
        output.write_text(v10_stable_milestone_report(db)["content"], encoding="utf-8")
    finally:
        db.close()
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
