from __future__ import annotations

import sys
from pathlib import Path

from dry_run_migration_sql import generate_sql
from migration_check import inspect_database


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    if not db_path.exists():
        print(f"POST MIGRATION VERIFY FAILED: database not found: {db_path}")
        return 2
    rows = inspect_database(db_path)
    remaining_sql = generate_sql(db_path)
    missing = [row for row in rows if row["missing"]]
    print("# v8.3 post-migration verification snapshot")
    print(f"Database: {db_path}")
    for row in rows:
        state = "PASS" if not row["missing"] else "MISSING"
        print(f"- {row['table']}: {state} ({', '.join(row['missing']) or 'none'})")
    print(f"Remaining SQL statements: {len(remaining_sql)}")
    if missing or remaining_sql:
        print("Result: FOLLOW-UP NEEDED")
        return 1
    print("Result: VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
