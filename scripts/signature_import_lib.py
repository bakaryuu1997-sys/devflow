from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from signing_readiness_lib import timestamp_handoff_package

HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")


def signed_import_package(db_path: Path) -> dict:
    package = timestamp_handoff_package(db_path)
    return {"version": "9.1", "status": "Ready for Signed Payload Import" if package["status"] == "Package Ready" else "Blocked", "payload_hash": package["payload_hash"], "manifest_hash": package["manifest_hash"], "bundle_hash": package["bundle_hash"]}


def verify_signed_payload(db_path: Path, payload_hash: str, signature_hash: str) -> dict:
    ensure_tables(db_path)
    package = signed_import_package(db_path)
    status = "Verified" if package["payload_hash"] == payload_hash and HEX64.match(signature_hash) else "Needs Review"
    with sqlite3.connect(db_path) as con:
        con.execute("""INSERT INTO signed_payload_verification_records (payload_hash, manifest_hash, bundle_hash, signature_algorithm, signer_name, signature_reference, signature_hash, verification_status, notes, content, created_at) VALUES (?, ?, ?, 'external-signature-hash', 'CLI Operator', 'CLI import', ?, ?, '', ?, CURRENT_TIMESTAMP)""", (payload_hash, package["manifest_hash"], package["bundle_hash"], signature_hash, status, render_signed_record(status, payload_hash)))
        con.commit()
    return {"version": "9.1", "status": status, "payload_hash": payload_hash, "signature_hash": signature_hash}


def timestamp_token_package(db_path: Path) -> dict:
    package = timestamp_handoff_package(db_path)
    return {"version": "9.1", "status": "Ready for Token Attachment" if package["payload_hash"] else "Blocked", "payload_hash": package["payload_hash"], "manifest_hash": package["manifest_hash"], "bundle_hash": package["bundle_hash"]}


def render_signed_package(data: dict) -> str:
    return f"# v9.1 Signed Payload Import Package\n\nStatus: {data['status']}\nPayload hash: `{data['payload_hash']}`\nManifest hash: `{data['manifest_hash']}`\n"


def render_token_package(data: dict) -> str:
    return f"# v9.1 Timestamp Token Evidence Package\n\nStatus: {data['status']}\nPayload hash: `{data['payload_hash']}`\n"


def render_signed_record(status: str, payload_hash: str) -> str:
    return f"# v9.1 Signed Payload Verification\n\nStatus: {status}\nPayload hash: `{payload_hash}`\n"


def ensure_tables(db_path: Path) -> None:
    with sqlite3.connect(db_path) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS signed_payload_verification_records (id INTEGER PRIMARY KEY, payload_hash TEXT NOT NULL, manifest_hash TEXT DEFAULT '', bundle_hash TEXT DEFAULT '', signature_algorithm TEXT DEFAULT '', signer_name TEXT DEFAULT '', signature_reference TEXT DEFAULT '', signature_hash TEXT DEFAULT '', verification_status TEXT DEFAULT '', notes TEXT DEFAULT '', content TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        con.execute("""CREATE TABLE IF NOT EXISTS timestamp_token_evidence_attachments (id INTEGER PRIMARY KEY, handoff_id INTEGER DEFAULT 0, payload_hash TEXT NOT NULL, token_hash TEXT DEFAULT '', timestamp_authority TEXT DEFAULT '', token_reference TEXT DEFAULT '', verification_status TEXT DEFAULT '', notes TEXT DEFAULT '', content TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        con.commit()
