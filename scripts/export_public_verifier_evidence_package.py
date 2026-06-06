from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import SessionLocal
from app.public_verifier_evidence_service import public_verifier_evidence_package


def main() -> int:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "PUBLIC_VERIFIER_EVIDENCE_PACKAGE.md")
    db = SessionLocal()
    try:
        data = public_verifier_evidence_package(db)
        out.write_text(data["content"], encoding="utf-8")
        print(f"wrote {out}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
