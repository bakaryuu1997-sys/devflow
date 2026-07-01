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

COLUMN_SQL = {
    "release_signoffs.snapshot_json": "ALTER TABLE release_signoffs ADD COLUMN snapshot_json TEXT DEFAULT '';",
    "release_learning_items.owner": "ALTER TABLE release_learning_items ADD COLUMN owner VARCHAR(160) DEFAULT '';",
    "release_learning_items.due_date": "ALTER TABLE release_learning_items ADD COLUMN due_date VARCHAR(40) DEFAULT '';",
}

TABLE_SQL = {
    "signed_rehearsal_artifacts": """CREATE TABLE IF NOT EXISTS signed_rehearsal_artifacts (
  id INTEGER NOT NULL PRIMARY KEY,
  artifact_type VARCHAR(80) DEFAULT 'production-rehearsal',
  operator_name VARCHAR(160) DEFAULT '',
  reviewer_name VARCHAR(160) DEFAULT '',
  signature_text VARCHAR(255) DEFAULT '',
  status VARCHAR(60) DEFAULT 'Signed',
  notes TEXT DEFAULT '',
  content TEXT DEFAULT '',
  created_at DATETIME
);""",
    "operator_approval_records": """CREATE TABLE IF NOT EXISTS operator_approval_records (
  id INTEGER NOT NULL PRIMARY KEY,
  signed_artifact_id INTEGER NOT NULL,
  approver_name VARCHAR(160) DEFAULT '',
  approval_phrase VARCHAR(160) DEFAULT '',
  status VARCHAR(60) DEFAULT 'Approved',
  approval_note TEXT DEFAULT '',
  content TEXT DEFAULT '',
  created_at DATETIME,
  FOREIGN KEY(signed_artifact_id) REFERENCES signed_rehearsal_artifacts (id)
);""",
    "evidence_manifest_records": """CREATE TABLE IF NOT EXISTS evidence_manifest_records (
  id INTEGER NOT NULL PRIMARY KEY,
  algorithm VARCHAR(40) DEFAULT 'sha256',
  manifest_hash VARCHAR(128) NOT NULL,
  bundle_hash VARCHAR(128) DEFAULT '',
  status VARCHAR(60) DEFAULT 'Frozen',
  artifact_count INTEGER DEFAULT 0,
  approval_count INTEGER DEFAULT 0,
  item_count INTEGER DEFAULT 0,
  notes TEXT DEFAULT '',
  content TEXT DEFAULT '',
  created_at DATETIME
);""",
    "external_timestamp_handoff_records": """CREATE TABLE IF NOT EXISTS external_timestamp_handoff_records (
  id INTEGER NOT NULL PRIMARY KEY,
  payload_hash VARCHAR(128) NOT NULL,
  manifest_hash VARCHAR(128) DEFAULT '',
  bundle_hash VARCHAR(128) DEFAULT '',
  timestamp_authority VARCHAR(160) DEFAULT '',
  request_reference VARCHAR(160) DEFAULT '',
  response_token_hash VARCHAR(128) DEFAULT '',
  status VARCHAR(60) DEFAULT 'Prepared',
  notes TEXT DEFAULT '',
  content TEXT DEFAULT '',
  created_at DATETIME
);""",
    "signed_payload_verification_records": """CREATE TABLE IF NOT EXISTS signed_payload_verification_records (id INTEGER PRIMARY KEY, payload_hash TEXT NOT NULL, manifest_hash TEXT DEFAULT '', bundle_hash TEXT DEFAULT '', signature_algorithm TEXT DEFAULT '', signer_name TEXT DEFAULT '', signature_reference TEXT DEFAULT '', signature_hash TEXT DEFAULT '', verification_status TEXT DEFAULT '', notes TEXT DEFAULT '', content TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP);""",
    "timestamp_token_evidence_attachments": """CREATE TABLE IF NOT EXISTS timestamp_token_evidence_attachments (id INTEGER PRIMARY KEY, handoff_id INTEGER DEFAULT 0, payload_hash TEXT NOT NULL, token_hash TEXT DEFAULT '', timestamp_authority TEXT DEFAULT '', token_reference TEXT DEFAULT '', verification_status TEXT DEFAULT '', notes TEXT DEFAULT '', content TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP);""",
    "public_verifier_evidence_attachments": """CREATE TABLE IF NOT EXISTS public_verifier_evidence_attachments (id INTEGER PRIMARY KEY, adapter TEXT DEFAULT 'ed25519-public-key', payload_hash TEXT NOT NULL, signature_hash TEXT DEFAULT '', public_key_hash TEXT DEFAULT '', signer_name TEXT DEFAULT '', key_reference TEXT DEFAULT '', evidence_reference TEXT DEFAULT '', verification_status TEXT DEFAULT 'Needs Review', gate_status TEXT DEFAULT 'Not Gate-Ready', findings TEXT DEFAULT '', notes TEXT DEFAULT '', content TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP);""",
    "scope_decision_audits": """CREATE TABLE IF NOT EXISTS scope_decision_audits (
  id INTEGER NOT NULL PRIMARY KEY,
  project_id INTEGER NOT NULL,
  learning_item_id INTEGER NOT NULL,
  old_status VARCHAR(40) DEFAULT '',
  new_status VARCHAR(40) DEFAULT '',
  reason TEXT DEFAULT '',
  created_at DATETIME,
  FOREIGN KEY(project_id) REFERENCES projects (id),
  FOREIGN KEY(learning_item_id) REFERENCES release_learning_items (id)
);""",
}

INDEX_SQL = {
    "scope_decision_audits": [
        "CREATE INDEX IF NOT EXISTS ix_scope_decision_audits_project_id ON scope_decision_audits (project_id);",
        "CREATE INDEX IF NOT EXISTS ix_scope_decision_audits_learning_item_id ON scope_decision_audits (learning_item_id);",
    ],
    "operator_approval_records": [
        "CREATE INDEX IF NOT EXISTS ix_operator_approval_records_signed_artifact_id ON operator_approval_records (signed_artifact_id);",
    ],
    "evidence_manifest_records": [
        "CREATE INDEX IF NOT EXISTS ix_evidence_manifest_records_manifest_hash ON evidence_manifest_records (manifest_hash);",
    ],
    "external_timestamp_handoff_records": [
        "CREATE INDEX IF NOT EXISTS ix_external_timestamp_handoff_records_payload_hash ON external_timestamp_handoff_records (payload_hash);",
    ],
    "signed_payload_verification_records": [
        "CREATE INDEX IF NOT EXISTS ix_signed_payload_verification_records_payload_hash ON signed_payload_verification_records (payload_hash);"
    ],
    "timestamp_token_evidence_attachments": [
        "CREATE INDEX IF NOT EXISTS ix_timestamp_token_evidence_attachments_payload_hash ON timestamp_token_evidence_attachments (payload_hash);"
    ],
    "public_verifier_evidence_attachments": [
        "CREATE INDEX IF NOT EXISTS ix_public_verifier_evidence_attachments_payload_hash ON public_verifier_evidence_attachments (payload_hash);"
    ],
}


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    if not db_path.exists():
        print(f"DRY RUN FAILED: database not found: {db_path}")
        return 2
    statements = generate_sql(db_path)
    print("-- v8.2 dry-run SQL migration")
    print(f"-- database: {db_path}")
    print("-- no SQL is applied by this script")
    if not statements:
        print("-- No SQL needed for current schema.")
        return 0
    for sql in statements:
        print(sql.rstrip() + "\n")
    return 0


def generate_sql(db_path: Path) -> list[str]:
    con = sqlite3.connect(db_path)
    try:
        tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        statements: list[str] = []
        for table, sql in TABLE_SQL.items():
            if table not in tables:
                statements.append(sql)
                statements.extend(INDEX_SQL.get(table, []))
        for table, columns in REQUIRED_SCHEMA.items():
            if table not in tables:
                continue
            existing = {row[1] for row in con.execute(f"PRAGMA table_info({table})")}
            for column in columns:
                key = f"{table}.{column}"
                if column not in existing and key in COLUMN_SQL:
                    statements.append(COLUMN_SQL[key])
        return statements
    finally:
        con.close()


if __name__ == "__main__":
    raise SystemExit(main())
