from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

from evidence_manifest_lib import build_manifest, latest_frozen_manifest


def signing_readiness(db_path: Path) -> dict:
    current = build_manifest(db_path)
    frozen = latest_frozen_manifest(db_path)
    blockers = _blockers(current, frozen)
    payload = _payload(current, frozen)
    return {
        "version": "9.0",
        "status": "Ready for External Signing" if not blockers else "Not Ready",
        "ready": not blockers,
        "algorithm": "sha256",
        "payload_hash": _hash_json(payload),
        "manifest_hash": current["manifest_hash"],
        "bundle_hash": current["bundle_hash"],
        "blockers": blockers,
        "canonical_payload": payload,
    }


def timestamp_handoff_package(db_path: Path) -> dict:
    readiness = signing_readiness(db_path)
    return {
        "version": "9.0",
        "status": "Package Ready" if readiness["ready"] else "Blocked",
        "payload_hash": readiness["payload_hash"],
        "manifest_hash": readiness["manifest_hash"],
        "bundle_hash": readiness["bundle_hash"],
        "canonical_payload": readiness["canonical_payload"],
        "readiness": readiness,
    }


def render_signing_readiness(data: dict) -> str:
    lines = ["# v9.0 Cryptographic Signing Readiness", "", f"Status: {data['status']}", f"Payload hash: `{data['payload_hash']}`", f"Manifest hash: `{data['manifest_hash']}`", f"Bundle hash: `{data['bundle_hash']}`", "", "## Blockers"]
    lines.extend(f"- {item}" for item in (data["blockers"] or ["No blockers."]))
    return "\n".join(lines).strip() + "\n"


def render_timestamp_handoff(data: dict) -> str:
    lines = ["# v9.0 External Timestamp Handoff Package", "", f"Status: {data['status']}", f"Payload hash: `{data['payload_hash']}`", "", "## Canonical payload", "```json", json.dumps(data["canonical_payload"], indent=2, sort_keys=True), "```"]
    return "\n".join(lines).strip() + "\n"


def ensure_handoff_table(db_path: Path) -> None:
    with sqlite3.connect(db_path) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS external_timestamp_handoff_records (
            id INTEGER NOT NULL PRIMARY KEY,
            payload_hash TEXT NOT NULL,
            manifest_hash TEXT DEFAULT '',
            bundle_hash TEXT DEFAULT '',
            timestamp_authority TEXT DEFAULT '',
            request_reference TEXT DEFAULT '',
            response_token_hash TEXT DEFAULT '',
            status TEXT DEFAULT 'Prepared',
            notes TEXT DEFAULT '',
            content TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        con.execute("CREATE INDEX IF NOT EXISTS ix_external_timestamp_handoff_records_payload_hash ON external_timestamp_handoff_records (payload_hash)")
        con.commit()


def _blockers(current: dict, frozen: dict | None) -> list[str]:
    blockers = []
    if current["item_count"] == 0:
        blockers.append("No evidence items exist yet.")
    if not frozen:
        blockers.append("No frozen evidence manifest exists yet.")
    elif frozen.get("manifest_hash") != current["manifest_hash"] or frozen.get("bundle_hash") != current["bundle_hash"]:
        blockers.append("Current evidence differs from the latest frozen manifest.")
    return blockers


def _payload(current: dict, frozen: dict | None) -> dict[str, Any]:
    return {
        "schema_version": "9.0",
        "purpose": "external-signing-and-timestamp-handoff",
        "algorithm": "sha256",
        "manifest_hash": current["manifest_hash"],
        "bundle_hash": current["bundle_hash"],
        "frozen_manifest_id": frozen.get("id") if frozen else None,
        "frozen_manifest_hash": frozen.get("manifest_hash", "") if frozen else "",
        "frozen_bundle_hash": frozen.get("bundle_hash", "") if frozen else "",
        "item_count": current["item_count"],
    }


def _hash_json(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
