from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any


def connect(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    return con


def table_exists(con: sqlite3.Connection, table: str) -> bool:
    row = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
    return row is not None


def build_manifest(db_path: Path) -> dict:
    with connect(db_path) as con:
        artifacts = _rows(con, "signed_rehearsal_artifacts")
        approvals = _rows(con, "operator_approval_records")
        items = [_item("signed_rehearsal_artifacts", row) for row in artifacts]
        items.extend(_item("operator_approval_records", row) for row in approvals)
    manifest_hash = _hash_json({"items": items})
    bundle_hash = _hash_text(_bundle_source(items, manifest_hash))
    return {"version": "8.9", "algorithm": "sha256", "item_count": len(items), "artifact_count": len(artifacts), "approval_count": len(approvals), "manifest_hash": manifest_hash, "bundle_hash": bundle_hash, "items": items}


def latest_frozen_manifest(db_path: Path) -> dict | None:
    with connect(db_path) as con:
        if not table_exists(con, "evidence_manifest_records"):
            return None
        row = con.execute("SELECT * FROM evidence_manifest_records ORDER BY id DESC LIMIT 1").fetchone()
    return dict(row) if row else None


def render_manifest(data: dict) -> str:
    lines = ["# v8.9 Evidence Manifest", "", f"Algorithm: {data['algorithm']}", f"Manifest hash: `{data['manifest_hash']}`", f"Bundle hash: `{data['bundle_hash']}`", f"Items: {data['item_count']}", "", "## Items"]
    lines.extend(f"- {item['table']}#{item['id']} status={item['status']} hash={item['record_hash']}" for item in data["items"])
    if not data["items"]:
        lines.append("- No signed evidence or approval records found.")
    return "\n".join(lines).strip() + "\n"


def _rows(con: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    if not table_exists(con, table):
        return []
    return list(con.execute(f"SELECT * FROM {table} ORDER BY id ASC"))


def _item(table: str, row: sqlite3.Row) -> dict:
    payload = {key: row[key] for key in row.keys() if key != "id"}
    return {"table": table, "id": row["id"], "status": payload.get("status", ""), "created_at": payload.get("created_at", ""), "record_hash": _hash_json(payload)}


def _hash_json(value: Any) -> str:
    return _hash_text(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _bundle_source(items: list[dict], manifest_hash: str) -> str:
    rows = [manifest_hash]
    rows.extend(f"{item['table']}:{item['id']}:{item['record_hash']}" for item in items)
    return "\n".join(rows)
