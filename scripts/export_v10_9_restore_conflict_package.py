import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.profile_restore_conflict_service import v10_9_operator_restore_conflict_package


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("v10_9_restore_conflict_package.md")
    profile_id = sys.argv[2] if len(sys.argv) > 2 else "core-risk"
    db = SessionLocal()
    try:
        package = v10_9_operator_restore_conflict_package(db, profile_id)
    finally:
        db.close()
    output.write_text(package["content"], encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
