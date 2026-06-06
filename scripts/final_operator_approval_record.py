from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

APPROVAL_PHRASE = "I_APPROVE_PRODUCTION_MIGRATION"


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("FINAL_OPERATOR_APPROVAL_RECORD.md")
    if not db_path.exists():
        print(f"APPROVAL RECORD BLOCKED: database not found: {db_path}")
        return 2
    out_path.write_text(build_record(db_path), encoding="utf-8")
    print(f"FINAL OPERATOR APPROVAL RECORD EXPORTED: {out_path}")
    return 0


def build_record(db_path: Path) -> str:
    tables = table_names(db_path)
    signed_count = count_rows(db_path, "signed_rehearsal_artifacts") if "signed_rehearsal_artifacts" in tables else 0
    approval_count = count_rows(db_path, "operator_approval_records") if "operator_approval_records" in tables else 0
    status = "Ready for final approval" if signed_count else "Blocked until a signed rehearsal artifact exists"
    lines = [
        "# v8.8 final operator approval record",
        "",
        f"Status: {status}",
        f"Signed artifact count: {signed_count}",
        f"Approval record count: {approval_count}",
        f"Approval phrase: `{APPROVAL_PHRASE}`",
        "",
        "## Final checks",
        "- [ ] Signed rehearsal artifact exists",
        "- [ ] Operator and reviewer names are recorded",
        "- [ ] Approval phrase is typed by a human approver",
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
