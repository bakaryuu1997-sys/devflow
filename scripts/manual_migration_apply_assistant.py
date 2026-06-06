from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

from dry_run_migration_sql import generate_sql


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    if not db_path.exists():
        print(f"APPLY ASSISTANT FAILED: database not found: {db_path}")
        return 2
    statements = generate_sql(db_path)
    print("# v8.3 manual migration apply assistant")
    print(f"Database: {db_path}")
    print("This script does not apply SQL automatically.")
    if not statements:
        print("Status: Already migrated")
        print("Next: python scripts/post_migration_verify.py devflow.db")
        return 0
    print("Status: Manual apply required")
    print("Steps:")
    for step in apply_steps(db_path):
        print(f"- {step}")
    print("\nSQL:")
    print(sql_script(statements))
    return 1


def apply_steps(db_path: Path) -> list[str]:
    backup = db_path.with_suffix(db_path.suffix + ".backup")
    return [
        "Stop the app and background terminals.",
        f"Copy {db_path} to {backup}.",
        "Apply the SQL below to a copied database first.",
        "Apply it to the real database only after the copy verifies.",
        "Run python scripts/post_migration_verify.py devflow.db.",
    ]


def sql_script(statements: list[str]) -> str:
    lines = ["BEGIN TRANSACTION;"]
    lines.extend(sql.rstrip() for sql in statements)
    lines.append("COMMIT;")
    return "\n".join(lines).strip()


if __name__ == "__main__":
    raise SystemExit(main())
