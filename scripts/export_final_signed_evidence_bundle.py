from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import SessionLocal
from app.final_evidence_bundle_service import final_signed_release_bundle_package


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("FINAL_SIGNED_EVIDENCE_BUNDLE.md")
    db = SessionLocal()
    try:
        output.write_text(final_signed_release_bundle_package(db)["content"], encoding="utf-8")
    finally:
        db.close()
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
