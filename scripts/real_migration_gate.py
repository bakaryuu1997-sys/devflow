from __future__ import annotations

import shutil
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

from dry_run_migration_sql import generate_sql
from migration_check import inspect_database

APPROVAL_PHRASE = "I_APPROVE_PRODUCTION_MIGRATION"


def main() -> int:
    db_path, approved = parse_args(sys.argv[1:])
    if not db_path.exists():
        print(f"REAL MIGRATION BLOCKED: database not found: {db_path}")
        return 2
    statements = generate_sql(db_path)
    print("# v8.5 human-approved real migration gate")
    print(f"Database: {db_path}")
    print(f"Pending SQL statements: {len(statements)}")
    if not statements:
        print("Result: NO MIGRATION NEEDED")
        return 0
    if not approved:
        print("Result: BLOCKED - human approval required")
        print(f"Run again with: --approve {APPROVAL_PHRASE}")
        return 3
    backup = backup_path(db_path)
    shutil.copy2(db_path, backup)
    try:
        apply_sql(db_path, statements)
    except Exception as exc:
        shutil.copy2(backup, db_path)
        print(f"Result: FAILED AND RESTORED FROM BACKUP: {exc}")
        return 1
    missing = [row for row in inspect_database(db_path) if row["missing"]]
    print(f"Backup: {backup}")
    if missing:
        print("Result: APPLY FINISHED BUT VERIFICATION FAILED")
        return 1
    print("Result: PRODUCTION MIGRATION VERIFIED")
    return 0


def parse_args(args: list[str]) -> tuple[Path, bool]:
    db_path = Path(args[0] if args else "devflow.db")
    approved = len(args) >= 3 and args[1] == "--approve" and args[2] == APPROVAL_PHRASE
    return db_path, approved


def backup_path(db_path: Path) -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    return db_path.with_name(f"{db_path.stem}.v8_5_prod_backup_{stamp}{db_path.suffix}")


def apply_sql(db_path: Path, statements: list[str]) -> None:
    con = sqlite3.connect(db_path)
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
