from __future__ import annotations
import re
from sqlalchemy.orm import Session
from app.crypto_signing_service import cryptographic_signing_readiness, timestamp_handoff_integrity_check
from app.models_v90 import ExternalTimestampHandoffRecord
from app.models_v91 import SignedPayloadVerificationRecord, TimestampTokenEvidenceAttachment
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")

def signed_payload_import_package(db: Session) -> dict:
    readiness = cryptographic_signing_readiness(db)
    data = {
        "version": "9.1",
        "mode": "signed-payload-import-package",
        "status": "Ready for Signed Payload Import" if readiness["ready"] else "Blocked",
        "ready": readiness["ready"],
        "payload_hash": readiness["payload_hash"],
        "manifest_hash": readiness["manifest_hash"],
        "bundle_hash": readiness["bundle_hash"],
        "required_fields": ["payload_hash", "signature_hash", "signer_name", "signature_reference"],
        "validation_rules": _signature_rules(),
        "readiness": readiness,
    }
    data["content"] = _signed_import_markdown(data)
    return data


def create_signed_payload_verification(db: Session, payload: dict) -> dict:
    package = signed_payload_import_package(db)
    payload_hash = (payload.get("payload_hash") or "").strip()
    signature_hash = (payload.get("signature_hash") or "").strip()
    status = _signature_status(package, payload_hash, signature_hash)
    record = SignedPayloadVerificationRecord(
        payload_hash=payload_hash,
        manifest_hash=package["manifest_hash"],
        bundle_hash=package["bundle_hash"],
        signature_algorithm=(payload.get("signature_algorithm") or "external-signature-hash").strip(),
        signer_name=(payload.get("signer_name") or "").strip(),
        signature_reference=(payload.get("signature_reference") or "").strip(),
        signature_hash=signature_hash,
        verification_status=status,
        notes=(payload.get("notes") or "").strip(),
    )
    record.content = _signed_record_markdown(_signed_record_row(record))
    db.add(record)
    db.commit()
    db.refresh(record)
    return _signed_record_row(record)


def list_signed_payload_verifications(db: Session) -> dict:
    rows = db.query(SignedPayloadVerificationRecord).order_by(SignedPayloadVerificationRecord.id.desc()).all()
    data = {"version": "9.1", "mode": "signed-payload-verifications", "count": len(rows), "records": [_signed_record_row(row) for row in rows]}
    data["content"] = _signed_list_markdown(data)
    return data


def timestamp_token_evidence_package(db: Session) -> dict:
    integrity = timestamp_handoff_integrity_check(db)
    latest = _latest_handoff(db)
    data = {
        "version": "9.1",
        "mode": "timestamp-token-evidence-package",
        "status": "Ready for Token Attachment" if latest else "No Handoff Record",
        "ready": bool(latest),
        "handoff_id": latest.id if latest else None,
        "payload_hash": latest.payload_hash if latest else integrity.get("current_payload_hash", ""),
        "timestamp_authority": latest.timestamp_authority if latest else "",
        "required_fields": ["payload_hash", "token_hash", "timestamp_authority", "token_reference"],
        "validation_rules": _token_rules(),
        "handoff_integrity": integrity,
    }
    data["content"] = _token_package_markdown(data)
    return data


def attach_timestamp_token_evidence(db: Session, payload: dict) -> dict:
    package = timestamp_token_evidence_package(db)
    token_hash = (payload.get("token_hash") or "").strip()
    payload_hash = (payload.get("payload_hash") or package["payload_hash"] or "").strip()
    status = _token_status(package, payload_hash, token_hash)
    record = TimestampTokenEvidenceAttachment(
        handoff_id=int(package["handoff_id"] or 0),
        payload_hash=payload_hash,
        token_hash=token_hash,
        timestamp_authority=(payload.get("timestamp_authority") or package["timestamp_authority"] or "External TSA").strip(),
        token_reference=(payload.get("token_reference") or "").strip(),
        verification_status=status,
        notes=(payload.get("notes") or "").strip(),
    )
    record.content = _token_record_markdown(_token_record_row(record))
    db.add(record)
    db.commit()
    db.refresh(record)
    return _token_record_row(record)


def list_timestamp_token_evidence(db: Session) -> dict:
    rows = db.query(TimestampTokenEvidenceAttachment).order_by(TimestampTokenEvidenceAttachment.id.desc()).all()
    data = {"version": "9.1", "mode": "timestamp-token-evidence-attachments", "count": len(rows), "records": [_token_record_row(row) for row in rows]}
    data["content"] = _token_list_markdown(data)
    return data

def signed_payload_timestamp_integrity_check(db: Session) -> dict:
    package = signed_payload_import_package(db)
    latest_signed = db.query(SignedPayloadVerificationRecord).order_by(SignedPayloadVerificationRecord.id.desc()).first()
    latest_token = db.query(TimestampTokenEvidenceAttachment).order_by(TimestampTokenEvidenceAttachment.id.desc()).first()
    signed_ok = bool(latest_signed and latest_signed.payload_hash == package["payload_hash"] and latest_signed.verification_status == "Verified")
    token_ok = bool(latest_token and latest_token.payload_hash == package["payload_hash"] and latest_token.verification_status == "Verified")
    data = {
        "version": "9.1",
        "mode": "signed-payload-timestamp-integrity-check",
        "status": "Verified" if signed_ok and token_ok else "Needs Evidence",
        "verified": signed_ok and token_ok,
        "current_payload_hash": package["payload_hash"],
        "signed_payload_verified": signed_ok,
        "timestamp_token_verified": token_ok,
        "latest_signed_payload": _signed_record_row(latest_signed) if latest_signed else None,
        "latest_timestamp_token": _token_record_row(latest_token) if latest_token else None,
    }
    data["content"] = _integrity_markdown(data)
    return data


def _latest_handoff(db: Session) -> ExternalTimestampHandoffRecord | None:
    return db.query(ExternalTimestampHandoffRecord).order_by(ExternalTimestampHandoffRecord.id.desc()).first()


def _signature_status(package: dict, payload_hash: str, signature_hash: str) -> str:
    if not package["ready"]:
        return "Blocked"
    if payload_hash != package["payload_hash"]:
        return "Payload Hash Mismatch"
    if not HEX64.match(signature_hash):
        return "Invalid Signature Hash"
    return "Verified"


def _token_status(package: dict, payload_hash: str, token_hash: str) -> str:
    if not package["ready"]:
        return "Blocked"
    if payload_hash != package["payload_hash"]:
        return "Payload Hash Mismatch"
    if not HEX64.match(token_hash):
        return "Invalid Token Hash"
    return "Verified"


def _signature_rules() -> list[str]:
    return ["payload_hash must match the current canonical payload hash.", "signature_hash must be a 64-character SHA-256 style hex digest.", "Store only signature references or hashes; do not store private keys in the app."]


def _token_rules() -> list[str]:
    return ["payload_hash must match the handoff payload hash.", "token_hash must be a 64-character SHA-256 style hex digest.", "Keep the external timestamp token file outside the app and store a reference here."]


def _signed_record_row(row: SignedPayloadVerificationRecord) -> dict:
    return {"id": row.id, "payload_hash": row.payload_hash, "manifest_hash": row.manifest_hash, "bundle_hash": row.bundle_hash, "signature_algorithm": row.signature_algorithm, "signer_name": row.signer_name, "signature_reference": row.signature_reference, "signature_hash": row.signature_hash, "verification_status": row.verification_status, "notes": row.notes, "created_at": row.created_at.isoformat() if row.created_at else "", "content": row.content}


def _token_record_row(row: TimestampTokenEvidenceAttachment) -> dict:
    return {"id": row.id, "handoff_id": row.handoff_id, "payload_hash": row.payload_hash, "token_hash": row.token_hash, "timestamp_authority": row.timestamp_authority, "token_reference": row.token_reference, "verification_status": row.verification_status, "notes": row.notes, "created_at": row.created_at.isoformat() if row.created_at else "", "content": row.content}


def _signed_import_markdown(data: dict) -> str:
    lines = ["# v9.1 Signed Payload Import Package", "", f"Status: {data['status']}", f"Payload hash: `{data['payload_hash']}`", "", "## Required fields"]
    lines.extend(f"- {field}" for field in data["required_fields"])
    lines.extend(["", "## Validation rules", *[f"- {rule}" for rule in data["validation_rules"]]])
    return "\n".join(lines).strip() + "\n"


def _signed_record_markdown(row: dict) -> str:
    return f"# v9.1 Signed Payload Verification\n\nStatus: {row['verification_status']}\nPayload hash: `{row['payload_hash']}`\nSigner: {row['signer_name']}\nReference: {row['signature_reference']}\n"


def _signed_list_markdown(data: dict) -> str:
    lines = ["# v9.1 Signed Payload Verifications", "", f"Count: {data['count']}"]
    lines.extend(f"- #{row['id']} {row['verification_status']} signer={row['signer_name']} payload={row['payload_hash']}" for row in data["records"])
    return "\n".join(lines).strip() + "\n"


def _token_package_markdown(data: dict) -> str:
    lines = ["# v9.1 Timestamp Token Evidence Package", "", f"Status: {data['status']}", f"Payload hash: `{data['payload_hash']}`", f"Handoff id: {data['handoff_id'] or 'none'}", "", "## Validation rules"]
    lines.extend(f"- {rule}" for rule in data["validation_rules"])
    return "\n".join(lines).strip() + "\n"


def _token_record_markdown(row: dict) -> str:
    return f"# v9.1 Timestamp Token Evidence Attachment\n\nStatus: {row['verification_status']}\nPayload hash: `{row['payload_hash']}`\nToken reference: {row['token_reference']}\n"


def _token_list_markdown(data: dict) -> str:
    lines = ["# v9.1 Timestamp Token Evidence Attachments", "", f"Count: {data['count']}"]
    lines.extend(f"- #{row['id']} {row['verification_status']} authority={row['timestamp_authority']} payload={row['payload_hash']}" for row in data["records"])
    return "\n".join(lines).strip() + "\n"


def _integrity_markdown(data: dict) -> str:
    return f"# v9.1 Signed Payload + Timestamp Integrity Check\n\nStatus: {data['status']}\nVerified: {data['verified']}\nSigned payload verified: {data['signed_payload_verified']}\nTimestamp token verified: {data['timestamp_token_verified']}\n"
