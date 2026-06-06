from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.recovery_ux_fixture_service import v11_1_operator_fixture_package


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("v11_1_operator_fixture_package.md")
    profile_id = sys.argv[2] if len(sys.argv) > 2 else "core-risk"
    db = SessionLocal()
    try:
        package = v11_1_operator_fixture_package(db, profile_id)
    finally:
        db.close()
    output.write_text(package["content"], encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
