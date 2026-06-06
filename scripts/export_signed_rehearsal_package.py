from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REQUIRED_SIGNATURE = "I ran and reviewed the production upgrade rehearsal on a copied database."


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("SIGNED_REHEARSAL_PACKAGE.md")
    if not db_path.exists():
        print(f"SIGNED PACKAGE BLOCKED: database not found: {db_path}")
        return 2
    out_path.write_text(build_package(db_path), encoding="utf-8")
    print(f"SIGNED REHEARSAL PACKAGE EXPORTED: {out_path}")
    return 0


def build_package(db_path: Path) -> str:
    tables = table_names(db_path)
    has_storage = "signed_rehearsal_artifacts" in tables
    artifact_count = count_rows(db_path, "signed_rehearsal_artifacts") if has_storage else 0
    lines = [
        "# v8.8 signed rehearsal artifact package",
        "",
        f"Database: {db_path}",
        f"Artifact storage ready: {has_storage}",
        f"Stored artifact count: {artifact_count}",
        f"Required signature: {REQUIRED_SIGNATURE}",
        "",
        "## Operator fields",
        "- [ ] Operator name recorded",
        "- [ ] Reviewer name recorded",
        "- [ ] Rehearsal report attached",
        "- [ ] Required signature text confirmed",
    ]
    return "\n".join(lines).strip() + "\n"


def table_names(db_path: Path) -> set[str]:
    con = sqlite3.connect(db_path)
    try:
        return {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        con.close()


def count_rows(db_path: Path, table: str) -> int:
    con = sqlite3.connect(db_path)
    try:
        return int(con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
    finally:
        con.close()


if __name__ == "__main__":
    raise SystemExit(main())
