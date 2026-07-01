import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.database import SessionLocal
from app.final_release_tag_service import v11_9_operator_final_release_package


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("v11_9_final_release_package.md")
    profile_id = sys.argv[2] if len(sys.argv) > 2 else "core-risk"
    with SessionLocal() as db:
        package = v11_9_operator_final_release_package(db, profile_id)
    output.write_text(package["content"], encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
