from __future__ import annotations

import hashlib
import json
from typing import Any

from sqlalchemy.orm import Session

from app.evidence_manifest_service import current_evidence_manifest, export_bundle_integrity_check
from app.models_v89 import EvidenceManifestRecord
from app.models_v90 import ExternalTimestampHandoffRecord


def cryptographic_signing_readiness(db: Session) -> dict:
    current = current_evidence_manifest(db)
    integrity = export_bundle_integrity_check(db)
    latest = _latest_frozen(db)
    blockers = _readiness_blockers(current, integrity, latest)
    payload = _canonical_payload(current, latest)
    data = {
        "version": "9.0",
        "mode": "cryptographic-signing-readiness",
        "status": "Ready for External Signing" if not blockers else "Not Ready",
        "ready": not blockers,
        "algorithm": "sha256",
        "payload_hash": _hash_json(payload),
        "manifest_hash": current["manifest_hash"],
        "bundle_hash": current["bundle_hash"],
        "frozen_manifest_id": latest.id if latest else None,
        "blockers": blockers,
        "operator_steps": _operator_steps(blockers),
        "canonical_payload": payload,
    }
    data["content"] = _readiness_markdown(data)
    return data


def external_timestamp_handoff_package(db: Session) -> dict:
    readiness = cryptographic_signing_readiness(db)
    data = {
        "version": "9.0",
        "mode": "external-timestamp-handoff-package",
        "status": "Package Ready" if readiness["ready"] else "Blocked",
        "ready": readiness["ready"],
        "payload_hash": readiness["payload_hash"],
        "manifest_hash": readiness["manifest_hash"],
        "bundle_hash": readiness["bundle_hash"],
        "canonical_payload": readiness["canonical_payload"],
        "handoff_steps": _handoff_steps(readiness),
        "readiness": readiness,
    }
    data["content"] = _handoff_markdown(data)
    return data


def create_timestamp_handoff(db: Session, payload: dict) -> dict:
    package = external_timestamp_handoff_package(db)
    token_hash = (payload.get("response_token_hash") or "").strip()
    record = ExternalTimestampHandoffRecord(
        payload_hash=package["payload_hash"],
        manifest_hash=package["manifest_hash"],
        bundle_hash=package["bundle_hash"],
        timestamp_authority=(payload.get("timestamp_authority") or "External TSA").strip(),
        request_reference=(payload.get("request_reference") or "").strip(),
        response_token_hash=token_hash,
        status="Timestamped" if token_hash else "Prepared",
        notes=(payload.get("notes") or "").strip(),
        content=package["content"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _record_row(record)


def list_timestamp_handoffs(db: Session) -> dict:
    rows = db.query(ExternalTimestampHandoffRecord).order_by(ExternalTimestampHandoffRecord.id.desc()).all()
    data = {"version": "9.0", "mode": "external-timestamp-handoffs", "count": len(rows), "records": [_record_row(row) for row in rows]}
    data["content"] = _handoff_list_markdown(data)
    return data


def timestamp_handoff_integrity_check(db: Session) -> dict:
    package = external_timestamp_handoff_package(db)
    latest = db.query(ExternalTimestampHandoffRecord).order_by(ExternalTimestampHandoffRecord.id.desc()).first()
    match = bool(latest and latest.payload_hash == package["payload_hash"] and latest.bundle_hash == package["bundle_hash"])
    data = {
        "version": "9.0",
        "mode": "timestamp-handoff-integrity-check",
        "status": "Verified" if match else "No Matching Handoff",
        "verified": match,
        "current_payload_hash": package["payload_hash"],
        "handoff_payload_hash": latest.payload_hash if latest else "",
        "current_bundle_hash": package["bundle_hash"],
        "handoff_bundle_hash": latest.bundle_hash if latest else "",
        "latest_handoff": _record_row(latest) if latest else None,
    }
    data["content"] = _integrity_markdown(data)
    return data


def _latest_frozen(db: Session) -> EvidenceManifestRecord | None:
    return db.query(EvidenceManifestRecord).order_by(EvidenceManifestRecord.id.desc()).first()


def _readiness_blockers(current: dict, integrity: dict, latest: EvidenceManifestRecord | None) -> list[str]:
    blockers = []
    if current["item_count"] == 0:
        blockers.append("No signed rehearsal or operator approval evidence exists yet.")
    if latest is None:
        blockers.append("Freeze an evidence manifest before external signing or timestamp handoff.")
    if not integrity.get("verified"):
        blockers.append("Current evidence bundle does not match the latest frozen manifest.")
    return blockers


def _canonical_payload(current: dict, latest: EvidenceManifestRecord | None) -> dict[str, Any]:
    return {
        "schema_version": "9.0",
        "purpose": "external-signing-and-timestamp-handoff",
        "algorithm": "sha256",
        "manifest_hash": current["manifest_hash"],
        "bundle_hash": current["bundle_hash"],
        "frozen_manifest_id": latest.id if latest else None,
        "frozen_manifest_hash": latest.manifest_hash if latest else "",
        "frozen_bundle_hash": latest.bundle_hash if latest else "",
        "item_count": current["item_count"],
    }


def _operator_steps(blockers: list[str]) -> list[str]:
    if blockers:
        return ["Resolve all blockers first.", "Freeze evidence again after any evidence changes.", "Re-run bundle integrity check."]
    return ["Export the canonical payload.", "Submit payload_hash to the external signing or timestamp authority.", "Store the returned token hash/reference in DevFlow Guard."]


def _handoff_steps(readiness: dict) -> list[str]:
    if not readiness["ready"]:
        return ["Open Cryptographic Signing Readiness and fix blockers first."]
    return ["Export this handoff package.", "Send only the payload hash to the external timestamp service if policy allows.", "Record request reference and returned token hash.", "Run timestamp handoff integrity check."]


def _hash_json(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def _record_row(row: ExternalTimestampHandoffRecord) -> dict:
    return {"id": row.id, "status": row.status, "payload_hash": row.payload_hash, "manifest_hash": row.manifest_hash, "bundle_hash": row.bundle_hash, "timestamp_authority": row.timestamp_authority, "request_reference": row.request_reference, "response_token_hash": row.response_token_hash, "notes": row.notes, "created_at": row.created_at.isoformat(), "content": row.content}


def _readiness_markdown(data: dict) -> str:
    lines = ["# v9.0 Cryptographic Signing Readiness", "", f"Status: {data['status']}", f"Payload hash: `{data['payload_hash']}`", f"Manifest hash: `{data['manifest_hash']}`", f"Bundle hash: `{data['bundle_hash']}`", "", "## Blockers"]
    lines.extend(f"- {item}" for item in (data["blockers"] or ["No blockers."]))
    lines.extend(["", "## Operator steps", *[f"- [ ] {step}" for step in data["operator_steps"]]])
    return "\n".join(lines).strip() + "\n"


def _handoff_markdown(data: dict) -> str:
    lines = ["# v9.0 External Timestamp Handoff Package", "", f"Status: {data['status']}", f"Payload hash: `{data['payload_hash']}`", "", "## Handoff steps"]
    lines.extend(f"- [ ] {step}" for step in data["handoff_steps"])
    lines.extend(["", "## Canonical payload", "```json", json.dumps(data["canonical_payload"], indent=2, sort_keys=True), "```"])
    return "\n".join(lines).strip() + "\n"


def _handoff_list_markdown(data: dict) -> str:
    lines = ["# v9.0 External Timestamp Handoff Records", "", f"Count: {data['count']}"]
    lines.extend(f"- #{row['id']} {row['status']} authority={row['timestamp_authority']} payload={row['payload_hash']}" for row in data["records"])
    return "\n".join(lines).strip() + "\n"


def _integrity_markdown(data: dict) -> str:
    lines = ["# v9.0 Timestamp Handoff Integrity Check", "", f"Status: {data['status']}", f"Verified: {data['verified']}", f"Current payload: `{data['current_payload_hash']}`", f"Handoff payload: `{data['handoff_payload_hash'] or 'none'}`"]
    return "\n".join(lines).strip() + "\n"
