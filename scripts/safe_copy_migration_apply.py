from __future__ import annotations

import shutil
import sqlite3
import sys
from pathlib import Path

from dry_run_migration_sql import generate_sql
from migration_check import inspect_database


def main() -> int:
    source = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    target = Path(sys.argv[2]) if len(sys.argv) > 2 else default_copy_path(source)
    if not source.exists():
        print(f"SAFE COPY MIGRATION FAILED: source database not found: {source}")
        return 2
    if source.resolve() == target.resolve():
        print("SAFE COPY MIGRATION FAILED: target copy must differ from source database")
        return 2
    shutil.copy2(source, target)
    before = source.stat().st_mtime_ns
    statements = generate_sql(target)
    if statements:
        apply_sql(target, statements)
    after = source.stat().st_mtime_ns
    if before != after:
        print("SAFE COPY MIGRATION FAILED: original database timestamp changed")
        return 3
    missing = [row for row in inspect_database(target) if row["missing"]]
    print("# v8.4 safe copy migration apply")
    print(f"Source: {source}")
    print(f"Copy: {target}")
    print(f"Applied statements: {len(statements)}")
    if missing:
        print("Result: COPY VERIFICATION FAILED")
        return 1
    print("Result: COPY MIGRATION VERIFIED")
    return 0


def default_copy_path(source: Path) -> Path:
    return source.with_name(f"{source.stem}.v8_4_migration_copy{source.suffix}")


def apply_sql(target: Path, statements: list[str]) -> None:
    con = sqlite3.connect(target)
    try:
        con.execute("BEGIN TRANSACTION")
        for statement in statements:
            con.execute(statement)
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


if __name__ == "__main__":
    raise SystemExit(main())
