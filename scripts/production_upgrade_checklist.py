from __future__ import annotations

import sys
from pathlib import Path

from dry_run_migration_sql import generate_sql
from migration_check import inspect_database

APPROVAL_PHRASE = "I_APPROVE_PRODUCTION_MIGRATION"


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    if not db_path.exists():
        print(f"PRODUCTION CHECKLIST BLOCKED: database not found: {db_path}")
        return 2
    statements = generate_sql(db_path)
    missing = [row for row in inspect_database(db_path) if row["missing"]]
    print("# v8.5 final production upgrade checklist")
    print(f"Database: {db_path}")
    print(f"Pending SQL statements: {len(statements)}")
    print("\n## Required steps")
    for item in checklist(db_path):
        print(f"- [ ] {item}")
    if not missing:
        print("\nResult: ALREADY READY")
        return 0
    print("\nResult: HUMAN REVIEW REQUIRED")
    return 1


def checklist(db_path: Path) -> list[str]:
    return [
        "Stop the app and confirm no process is writing to the database.",
        "Create a fresh backup and store it outside the app folder.",
        f"Run: python scripts/safe_copy_migration_apply.py {db_path} {db_path.with_suffix('.copy.db')}",
        f"Run: python scripts/rollback_drill.py {db_path}",
        f"Run: python scripts/real_migration_gate.py {db_path}",
        f"Apply only with explicit approval: --approve {APPROVAL_PHRASE}",
        f"Run: python scripts/post_migration_verify.py {db_path}",
        "Start the app and run smoke test before using production data.",
    ]


if __name__ == "__main__":
    raise SystemExit(main())
