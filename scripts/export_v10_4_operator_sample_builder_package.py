from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import SessionLocal
from app.sample_project_builder_service import v10_4_operator_sample_builder_package


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("V10_4_OPERATOR_SAMPLE_BUILDER_PACKAGE.md")
    db = SessionLocal()
    try:
        output.write_text(v10_4_operator_sample_builder_package(db)["content"], encoding="utf-8")
    finally:
        db.close()
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
