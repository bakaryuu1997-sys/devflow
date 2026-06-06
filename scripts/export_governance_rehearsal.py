from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import SessionLocal
from app.end_to_end_rehearsal_service import end_to_end_governance_rehearsal


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("GOVERNANCE_REHEARSAL.md")
    db = SessionLocal()
    try:
        output.write_text(end_to_end_governance_rehearsal(db)["content"], encoding="utf-8")
    finally:
        db.close()
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
