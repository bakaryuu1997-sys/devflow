from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REQUIRED_SCHEMA = {
    "release_signoffs": ["snapshot_json"],
    "release_learning_items": ["owner", "due_date"],
    "scope_decision_audits": ["project_id", "learning_item_id", "old_status", "new_status", "reason", "created_at"],
    "signed_rehearsal_artifacts": [
        "artifact_type",
        "operator_name",
        "reviewer_name",
        "signature_text",
        "status",
        "notes",
        "content",
        "created_at",
    ],
    "operator_approval_records": [
        "signed_artifact_id",
        "approver_name",
        "approval_phrase",
        "status",
        "approval_note",
        "content",
        "created_at",
    ],
    "evidence_manifest_records": [
        "algorithm",
        "manifest_hash",
        "bundle_hash",
        "status",
        "artifact_count",
        "approval_count",
        "item_count",
        "notes",
        "content",
        "created_at",
    ],
    "external_timestamp_handoff_records": [
        "payload_hash",
        "manifest_hash",
        "bundle_hash",
        "timestamp_authority",
        "request_reference",
        "response_token_hash",
        "status",
        "notes",
        "content",
        "created_at",
    ],
    "signed_payload_verification_records": [
        "payload_hash",
        "manifest_hash",
        "bundle_hash",
        "signature_algorithm",
        "signer_name",
        "signature_reference",
        "signature_hash",
        "verification_status",
        "notes",
        "content",
        "created_at",
    ],
    "timestamp_token_evidence_attachments": [
        "handoff_id",
        "payload_hash",
        "token_hash",
        "timestamp_authority",
        "token_reference",
        "verification_status",
        "notes",
        "content",
        "created_at",
    ],
    "public_verifier_evidence_attachments": [
        "adapter",
        "payload_hash",
        "signature_hash",
        "public_key_hash",
        "signer_name",
        "key_reference",
        "evidence_reference",
        "verification_status",
        "gate_status",
        "findings",
        "notes",
        "content",
        "created_at",
    ],
}


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    if not db_path.exists():
        print(f"MIGRATION CHECK FAILED: database not found: {db_path}")
        return 2
    rows = inspect_database(db_path)
    missing = [row for row in rows if row["missing"]]
    print(f"Database: {db_path}")
    for row in rows:
        state = "PASS" if not row["missing"] else "MISSING"
        print(f"- {row['table']}: {state} ({', '.join(row['missing']) or 'none'})")
    if missing:
        print("Result: MIGRATION NEEDED")
        print("Next: back up the DB, add missing tables/columns, then run tests and smoke check.")
        return 1
    print("Result: READY")
    return 0


def inspect_database(db_path: Path) -> list[dict]:
    con = sqlite3.connect(db_path)
    try:
        tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        return [table_result(con, tables, table, columns) for table, columns in REQUIRED_SCHEMA.items()]
    finally:
        con.close()


def table_result(con: sqlite3.Connection, tables: set[str], table: str, columns: list[str]) -> dict:
    if table not in tables:
        return {"table": table, "missing": columns}
    existing = {row[1] for row in con.execute(f"PRAGMA table_info({table})")}
    return {"table": table, "missing": [column for column in columns if column not in existing]}


if __name__ == "__main__":
    raise SystemExit(main())
