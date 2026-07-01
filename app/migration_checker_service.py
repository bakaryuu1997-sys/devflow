from __future__ import annotations

from sqlalchemy import inspect
from sqlalchemy.orm import Session

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
    "external_verifier_profiles": [
        "name",
        "adapter",
        "policy_preset",
        "key_reference",
        "status",
        "notes",
        "created_at",
    ],
    "final_signed_evidence_bundles": [
        "manifest_hash",
        "bundle_hash",
        "verifier_evidence_id",
        "profile_name",
        "status",
        "content",
        "created_at",
    ],
    "governance_rehearsal_records": ["status", "readiness_score", "blockers", "content", "created_at"],
}

OPTIONAL_HISTORY_FIELDS = {
    "release_learning_items": ["completed_at"],
    "scope_decision_audits": ["owner_before", "owner_after", "due_date_before", "due_date_after"],
}


def local_database_migration_check(db: Session) -> dict:
    inspector = inspect(db.get_bind())
    tables = set(inspector.get_table_names())
    table_rows = [_table_status(inspector, tables, table, cols) for table, cols in REQUIRED_SCHEMA.items()]
    optional_rows = [
        _optional_status(inspector, tables, table, cols) for table, cols in OPTIONAL_HISTORY_FIELDS.items()
    ]
    missing_tables = [row["table"] for row in table_rows if row["state"] == "MISSING_TABLE"]
    missing_columns = [row for row in table_rows if row["missing_columns"]]
    status = _status(missing_tables, missing_columns)
    data = {
        "version": "8.1",
        "status": status,
        "safe_to_upgrade": status in {"Ready", "Needs Optional Polish"},
        "required_schema": table_rows,
        "optional_schema": optional_rows,
        "missing_tables": missing_tables,
        "missing_column_count": sum(len(row["missing_columns"]) for row in table_rows),
        "backup_required": status != "Ready",
        "upgrade_steps": _steps(missing_tables, missing_columns),
        "action_hints": _hints(status, missing_tables, missing_columns),
    }
    data["content"] = _markdown(data)
    return data


def upgrade_safety_report(db: Session) -> dict:
    check = local_database_migration_check(db)
    risk_score = _risk_score(check)
    data = {
        "version": "8.1",
        "status": _risk_status(risk_score),
        "risk_score": risk_score,
        "safe_to_upgrade": check["safe_to_upgrade"] and risk_score < 70,
        "migration_check_status": check["status"],
        "backup_required": check["backup_required"],
        "must_fix_before_upgrade": _must_fix(check),
        "recommended_order": _recommended_order(check),
        "migration_check": check,
    }
    data["content"] = _safety_markdown(data)
    return data


def _table_status(inspector, tables: set[str], table: str, required_columns: list[str]) -> dict:
    if table not in tables:
        return {
            "table": table,
            "state": "MISSING_TABLE",
            "required_columns": required_columns,
            "missing_columns": required_columns,
        }
    existing = {col["name"] for col in inspector.get_columns(table)}
    missing = [name for name in required_columns if name not in existing]
    return {
        "table": table,
        "state": "PASS" if not missing else "MISSING_COLUMNS",
        "required_columns": required_columns,
        "missing_columns": missing,
    }


def _optional_status(inspector, tables: set[str], table: str, columns: list[str]) -> dict:
    if table not in tables:
        return {"table": table, "state": "NOT_AVAILABLE", "optional_columns": columns, "missing_columns": columns}
    existing = {col["name"] for col in inspector.get_columns(table)}
    missing = [name for name in columns if name not in existing]
    return {
        "table": table,
        "state": "PASS" if not missing else "OPTIONAL_MISSING",
        "optional_columns": columns,
        "missing_columns": missing,
    }


def _status(missing_tables: list[str], missing_columns: list[dict]) -> str:
    if missing_tables:
        return "Blocked"
    if missing_columns:
        return "Migration Needed"
    return "Ready"


def _steps(missing_tables: list[str], missing_columns: list[dict]) -> list[str]:
    steps = ["Back up the SQLite database before changing schema."]
    steps.extend(f"Create missing table: {table}." for table in missing_tables)
    for row in missing_columns:
        steps.extend(
            f"Add column {col} to {row['table']} with nullable/default-safe settings." for col in row["missing_columns"]
        )
    steps.append("Run quality_check, compileall, pytest, security_check, and HTTP smoke after migration.")
    return steps


def _hints(status: str, missing_tables: list[str], missing_columns: list[dict]) -> list[str]:
    if status == "Ready":
        return ["Schema is ready for v9.1 governance workflow checks.", "Keep a backup before future schema changes."]
    hints = []
    if missing_tables:
        hints.append("Create missing governance/audit tables before relying on v8.x approval history.")
    if missing_columns:
        hints.append("Add missing columns first; keep them nullable or default-empty for older rows.")
    hints.append("Do not delete old Markdown snapshots; structured JSON is additive.")
    return hints


def _risk_score(check: dict) -> int:
    score = check["missing_column_count"] * 20 + len(check["missing_tables"]) * 40
    return min(100, score)


def _risk_status(score: int) -> str:
    if score >= 70:
        return "High Upgrade Risk"
    if score > 0:
        return "Migration Review Needed"
    return "Upgrade Safe"


def _must_fix(check: dict) -> list[str]:
    fixes = [f"Create table {table}" for table in check["missing_tables"]]
    for row in check["required_schema"]:
        fixes.extend(f"Add {row['table']}.{col}" for col in row["missing_columns"])
    return fixes


def _recommended_order(check: dict) -> list[str]:
    return [
        "1. Backup database",
        "2. Apply additive schema changes",
        "3. Start app",
        "4. Run smoke tests",
        "5. Export governance readiness report",
    ] + check["upgrade_steps"]


def _markdown(data: dict) -> str:
    lines = [
        "# v8.1 Local Database Migration Check",
        "",
        f"Status: {data['status']}",
        f"Safe to upgrade: {data['safe_to_upgrade']}",
        "",
        "## Required schema",
    ]
    lines.extend(
        f"- {row['table']}: {row['state']} missing={', '.join(row['missing_columns']) or 'none'}"
        for row in data["required_schema"]
    )
    lines.extend(["", "## Upgrade steps"])
    lines.extend(f"- {step}" for step in data["upgrade_steps"])
    return "\n".join(lines).strip() + "\n"


def _safety_markdown(data: dict) -> str:
    lines = [
        "# v8.1 Upgrade Safety Report",
        "",
        f"Status: {data['status']} ({data['risk_score']}/100)",
        f"Safe to upgrade: {data['safe_to_upgrade']}",
        "",
        "## Must fix",
    ]
    fixes = data["must_fix_before_upgrade"] or ["No required schema fixes found."]
    lines.extend(f"- {fix}" for fix in fixes)
    lines.extend(["", "## Recommended order"])
    lines.extend(f"- {step}" for step in data["recommended_order"][:8])
    return "\n".join(lines).strip() + "\n"
