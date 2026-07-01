import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.profile_rollback_rehearsal_service import v10_7_operator_restore_package


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("v10_7_restore_rehearsal.md")
    profile_id = sys.argv[2] if len(sys.argv) > 2 else "core-risk"
    db = SessionLocal()
    try:
        package = v10_7_operator_restore_package(db, profile_id)
    finally:
        db.close()
    output.write_text(package["content"], encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
