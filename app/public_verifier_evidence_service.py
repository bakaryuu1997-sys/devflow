from __future__ import annotations

from sqlalchemy.orm import Session

from app.crypto_signing_service import cryptographic_signing_readiness
from app.models_v95 import PublicVerifierEvidenceAttachment
from app.public_key_verifier_service import public_key_verifier_dry_run, public_key_verifier_readiness


def public_verifier_evidence_package(db: Session) -> dict:
    readiness = public_key_verifier_readiness(db)
    signing = cryptographic_signing_readiness(db)
    data = {
        "version": "9.5",
        "mode": "public-verifier-evidence-package",
        "status": "Ready for Evidence Attachment" if readiness["ready"] else "Verifier Not Ready",
        "ready": readiness["ready"],
        "adapter": readiness["adapter"],
        "canonical_payload_hash": signing["payload_hash"],
        "required_fields": ["signer_name", "key_reference", "evidence_reference"],
        "rules": _attachment_rules(),
        "verifier_readiness": readiness,
    }
    data["content"] = _package_markdown(data)
    return data


def attach_public_verifier_evidence(db: Session, payload: dict) -> dict:
    verify_payload = payload.get("verification_payload") or {"use_fixture": True}
    result = public_key_verifier_dry_run(db, verify_payload)
    status = "Verified" if result["verified"] else result["status"]
    gate_status = "Gate-Ready" if result["verified"] else "Not Gate-Ready"
    record = PublicVerifierEvidenceAttachment(
        adapter=result["adapter"],
        payload_hash=result["payload_hash"],
        signature_hash=result["signature_hash"],
        public_key_hash=result["public_key_hash"],
        signer_name=(payload.get("signer_name") or "Fixture Operator").strip(),
        key_reference=(payload.get("key_reference") or "fixture-public-key").strip(),
        evidence_reference=(payload.get("evidence_reference") or "fixture-detached-signature").strip(),
        verification_status=status,
        gate_status=gate_status,
        findings="\n".join(result.get("findings") or []),
        notes=(payload.get("notes") or "").strip(),
    )
    record.content = _record_markdown(_row(record))
    db.add(record)
    db.commit()
    db.refresh(record)
    return _row(record)


def list_public_verifier_evidence(db: Session) -> dict:
    rows = db.query(PublicVerifierEvidenceAttachment).order_by(PublicVerifierEvidenceAttachment.id.desc()).all()
    data = {"version": "9.5", "mode": "public-verifier-evidence-attachments", "count": len(rows), "records": [_row(row) for row in rows]}
    data["content"] = _list_markdown(data)
    return data


def verified_signature_approval_gate(db: Session) -> dict:
    latest = db.query(PublicVerifierEvidenceAttachment).order_by(PublicVerifierEvidenceAttachment.id.desc()).first()
    signing = cryptographic_signing_readiness(db)
    verified = bool(latest and latest.verification_status == "Verified")
    blockers = _gate_blockers(latest, signing, verified)
    data = {
        "version": "9.5",
        "mode": "verified-signature-approval-gate",
        "status": "Gate Ready" if not blockers else "Blocked",
        "ready": not blockers,
        "canonical_payload_hash": signing["payload_hash"],
        "latest_evidence": _row(latest) if latest else None,
        "blockers": blockers,
        "approval_steps": _approval_steps(blockers),
    }
    data["content"] = _gate_markdown(data)
    return data


def _gate_blockers(latest: PublicVerifierEvidenceAttachment | None, signing: dict, verified: bool) -> list[str]:
    blockers = []
    if latest is None:
        blockers.append("Attach at least one public-key verifier evidence record.")
    elif not verified:
        blockers.append("Latest public verifier evidence is not Verified.")
    if not signing["ready"]:
        blockers.append("Cryptographic signing readiness is not ready.")
    return blockers


def _attachment_rules() -> list[str]:
    return [
        "Store public-key verification output only; never store private keys.",
        "Attach payload hash, public key hash, and detached signature hash to the release evidence.",
        "Approval gate may pass only after a real verifier returns Verified.",
    ]


def _approval_steps(blockers: list[str]) -> list[str]:
    if blockers:
        return ["Resolve blockers.", "Re-run public-key verifier dry-run.", "Attach verified evidence again."]
    return ["Freeze or export evidence bundle.", "Record operator approval with verified-signature gate evidence.", "Keep private keys outside DevFlow Guard."]


def _row(row: PublicVerifierEvidenceAttachment | None) -> dict:
    if row is None:
        return {}
    return {
        "id": row.id,
        "adapter": row.adapter,
        "payload_hash": row.payload_hash,
        "signature_hash": row.signature_hash,
        "public_key_hash": row.public_key_hash,
        "signer_name": row.signer_name,
        "key_reference": row.key_reference,
        "evidence_reference": row.evidence_reference,
        "verification_status": row.verification_status,
        "gate_status": row.gate_status,
        "findings": row.findings.splitlines() if row.findings else [],
        "notes": row.notes,
        "created_at": row.created_at.isoformat() if row.created_at else "",
        "content": row.content,
    }


def _package_markdown(data: dict) -> str:
    lines = ["# v9.5 Public Verifier Evidence Package", "", f"Status: {data['status']}", f"Adapter: {data['adapter']}", "", "## Rules"]
    lines.extend(f"- {rule}" for rule in data["rules"])
    return "\n".join(lines).strip() + "\n"


def _record_markdown(row: dict) -> str:
    return f"# v9.5 Public Verifier Evidence Attachment\n\nStatus: {row['verification_status']}\nGate: {row['gate_status']}\nPayload hash: `{row['payload_hash']}`\nSigner: {row['signer_name']}\n"


def _list_markdown(data: dict) -> str:
    lines = ["# v9.5 Public Verifier Evidence Attachments", "", f"Count: {data['count']}"]
    lines.extend(f"- #{row['id']} {row['verification_status']} signer={row['signer_name']} payload={row['payload_hash']}" for row in data["records"])
    return "\n".join(lines).strip() + "\n"


def _gate_markdown(data: dict) -> str:
    lines = ["# v9.5 Verified-Signature Approval Gate", "", f"Status: {data['status']}", f"Ready: {data['ready']}", "", "## Blockers"]
    lines.extend(f"- {item}" for item in (data["blockers"] or ["No blockers."]))
    lines.extend(["", "## Approval steps", *[f"- [ ] {step}" for step in data["approval_steps"]]])
    return "\n".join(lines).strip() + "\n"
