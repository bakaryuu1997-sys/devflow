from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.profile_reset_orchestrator_service import v10_5_operator_reset_package


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("v10_5_operator_reset_package.md")
    profile_id = sys.argv[2] if len(sys.argv) > 2 else "core-risk"
    db = SessionLocal()
    try:
        package = v10_5_operator_reset_package(db, profile_id)
    finally:
        db.close()
    output.write_text(package["content"], encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
