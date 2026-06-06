from __future__ import annotations
from sqlalchemy.orm import Session
from app.migration_checker_service import local_database_migration_check, upgrade_safety_report
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
    "signed_payload_verification_records": """CREATE TABLE IF NOT EXISTS signed_payload_verification_records (id INTEGER NOT NULL PRIMARY KEY, payload_hash VARCHAR(128) NOT NULL, manifest_hash VARCHAR(128) DEFAULT '', bundle_hash VARCHAR(128) DEFAULT '', signature_algorithm VARCHAR(80) DEFAULT 'external', signer_name VARCHAR(160) DEFAULT '', signature_reference VARCHAR(160) DEFAULT '', signature_hash VARCHAR(128) DEFAULT '', verification_status VARCHAR(80) DEFAULT 'Needs Review', notes TEXT DEFAULT '', content TEXT DEFAULT '', created_at DATETIME);""",
    "timestamp_token_evidence_attachments": """CREATE TABLE IF NOT EXISTS timestamp_token_evidence_attachments (id INTEGER NOT NULL PRIMARY KEY, handoff_id INTEGER DEFAULT 0, payload_hash VARCHAR(128) NOT NULL, token_hash VARCHAR(128) DEFAULT '', timestamp_authority VARCHAR(160) DEFAULT '', token_reference VARCHAR(160) DEFAULT '', verification_status VARCHAR(80) DEFAULT 'Needs Review', notes TEXT DEFAULT '', content TEXT DEFAULT '', created_at DATETIME);""",
    "external_verifier_profiles": """CREATE TABLE IF NOT EXISTS external_verifier_profiles (id INTEGER NOT NULL PRIMARY KEY, name VARCHAR(120) NOT NULL, adapter VARCHAR(80) DEFAULT 'ed25519-public-key', policy_preset VARCHAR(80) DEFAULT 'standard-release', key_reference VARCHAR(180) DEFAULT '', status VARCHAR(60) DEFAULT 'Active', notes TEXT DEFAULT '', created_at DATETIME);""",
    "final_signed_evidence_bundles": """CREATE TABLE IF NOT EXISTS final_signed_evidence_bundles (id INTEGER NOT NULL PRIMARY KEY, manifest_hash VARCHAR(128) NOT NULL, bundle_hash VARCHAR(128) NOT NULL, verifier_evidence_id INTEGER DEFAULT 0, profile_name VARCHAR(120) DEFAULT '', status VARCHAR(80) DEFAULT 'Draft', content TEXT DEFAULT '', created_at DATETIME);""",
    "governance_rehearsal_records": """CREATE TABLE IF NOT EXISTS governance_rehearsal_records (id INTEGER NOT NULL PRIMARY KEY, status VARCHAR(80) DEFAULT 'Needs Review', readiness_score INTEGER DEFAULT 0, blockers TEXT DEFAULT '', content TEXT DEFAULT '', created_at DATETIME);""",
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
    "external_verifier_profiles": ["CREATE UNIQUE INDEX IF NOT EXISTS ix_external_verifier_profiles_name ON external_verifier_profiles (name);"],
    "final_signed_evidence_bundles": ["CREATE INDEX IF NOT EXISTS ix_final_signed_evidence_bundles_bundle_hash ON final_signed_evidence_bundles (bundle_hash);"],
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
        "CREATE INDEX IF NOT EXISTS ix_signed_payload_verification_records_payload_hash ON signed_payload_verification_records (payload_hash);",
    ],
    "timestamp_token_evidence_attachments": [
        "CREATE INDEX IF NOT EXISTS ix_timestamp_token_evidence_attachments_payload_hash ON timestamp_token_evidence_attachments (payload_hash);",
    ],
}
def dry_run_sql_migration(db: Session) -> dict:
    check = local_database_migration_check(db)
    statements = _statements(check)
    data = {
        "version": "8.2",
        "mode": "dry-run",
        "status": "No SQL Needed" if not statements else "SQL Ready",
        "statement_count": len(statements),
        "will_apply_changes": False,
        "backup_required": bool(statements) or check["backup_required"],
        "migration_check_status": check["status"],
        "statements": statements,
        "apply_order": _apply_order(statements),
        "safety_notes": _safety_notes(statements),
        "migration_check": check,
    }
    data["content"] = _sql_markdown(data)
    return data
def backup_checklist(db: Session) -> dict:
    safety = upgrade_safety_report(db)
    data = {
        "version": "8.2",
        "status": "Backup Recommended" if safety["backup_required"] else "Backup Still Recommended",
        "backup_required": True,
        "database_target": "devflow.db or your configured SQLite path",
        "checklist": _backup_steps(safety),
        "verification_steps": _verify_steps(),
        "rollback_steps": _rollback_steps(),
        "upgrade_safety": safety,
    }
    data["content"] = _backup_markdown(data)
    return data
def _statements(check: dict) -> list[dict]:
    rows: list[dict] = []
    for table in check["missing_tables"]:
        if table in TABLE_SQL:
            rows.append(_row("create_table", table, TABLE_SQL[table]))
            for sql in INDEX_SQL.get(table, []):
                rows.append(_row("create_index", table, sql))
    for table_row in check["required_schema"]:
        table = table_row["table"]
        if table in check["missing_tables"]:
            continue
        for column in table_row["missing_columns"]:
            key = f"{table}.{column}"
            if key in COLUMN_SQL:
                rows.append(_row("add_column", key, COLUMN_SQL[key]))
    return rows
def _row(kind: str, target: str, sql: str) -> dict:
    return {"kind": kind, "target": target, "sql": sql, "safe_mode": "additive", "destructive": False}
def _apply_order(statements: list[dict]) -> list[str]:
    if not statements:
        return ["No schema SQL is needed for the current database."]
    return ["1. Stop the app", "2. Back up the SQLite database", "3. Review dry-run SQL", "4. Apply SQL manually", "5. Run migration_check.py", "6. Run tests and smoke check"]
def _safety_notes(statements: list[dict]) -> list[str]:
    notes = ["This endpoint never applies SQL automatically.", "Only additive CREATE/ALTER statements are generated."]
    if statements:
        notes.append("Review every statement against a copied database before touching production data.")
    return notes


def _backup_steps(safety: dict) -> list[str]:
    return [
        "Stop the local app and background terminals using the database.",
        "Copy the SQLite file to a timestamped backup path.",
        "Run the dry-run SQL generator and save the Markdown output.",
        "Test the generated SQL on a copied database first.",
        f"Confirm upgrade safety status: {safety['status']}.",
    ]


def _verify_steps() -> list[str]:
    return ["Run python scripts/migration_check.py devflow.db", "Start the app", "Open Governance Readiness", "Run HTTP smoke and pytest"]


def _rollback_steps() -> list[str]:
    return ["Stop the app", "Move the migrated DB aside", "Restore the timestamped backup", "Run migration_check.py again"]


def _sql_markdown(data: dict) -> str:
    lines = ["# v8.2 Dry-run SQL Migration", "", f"Status: {data['status']}", f"Will apply changes: {data['will_apply_changes']}", "", "## SQL"]
    if data["statements"]:
        lines.extend(f"```sql\n{row['sql']}\n```" for row in data["statements"])
    else:
        lines.append("No SQL needed for the current schema.")
    lines.extend(["", "## Safety notes"])
    lines.extend(f"- {note}" for note in data["safety_notes"])
    return "\n".join(lines).strip() + "\n"


def _backup_markdown(data: dict) -> str:
    lines = ["# v8.2 Backup Checklist", "", f"Status: {data['status']}", "", "## Checklist"]
    lines.extend(f"- [ ] {step}" for step in data["checklist"])
    lines.extend(["", "## Verification", *[f"- [ ] {step}" for step in data["verification_steps"]], "", "## Rollback"])
    lines.extend(f"- [ ] {step}" for step in data["rollback_steps"])
    return "\n".join(lines).strip() + "\n"
