from __future__ import annotations

from sqlalchemy.orm import Session

from app.crypto_signing_service import cryptographic_signing_readiness
from app.evidence_manifest_service import current_evidence_manifest, export_bundle_integrity_check
from app.models_v95 import PublicVerifierEvidenceAttachment


def verified_evidence_manifest_gate(db: Session) -> dict:
    signing = cryptographic_signing_readiness(db)
    manifest = current_evidence_manifest(db)
    integrity = export_bundle_integrity_check(db)
    evidence = db.query(PublicVerifierEvidenceAttachment).order_by(PublicVerifierEvidenceAttachment.id.desc()).first()
    blockers = _blockers(signing, integrity, evidence)
    data = {
        "version": "9.6",
        "mode": "verified-evidence-manifest-gate",
        "status": "Gate Ready" if not blockers else "Blocked",
        "ready": not blockers,
        "canonical_payload_hash": signing.get("payload_hash", ""),
        "manifest_hash": manifest.get("manifest_hash", ""),
        "bundle_hash": manifest.get("bundle_hash", ""),
        "latest_evidence": _evidence_row(evidence),
        "blockers": blockers,
        "hardening_rules": _rules(),
    }
    data["content"] = _markdown(data)
    return data


def _blockers(signing: dict, integrity: dict, evidence: PublicVerifierEvidenceAttachment | None) -> list[str]:
    blockers: list[str] = []
    if not signing.get("ready"):
        blockers.append("Cryptographic signing readiness is not ready.")
    if evidence is None:
        blockers.append("No public verifier evidence is attached.")
    elif evidence.verification_status != "Verified":
        blockers.append("Latest public verifier evidence is not Verified.")
    elif evidence.payload_hash != signing.get("payload_hash"):
        blockers.append("Verifier evidence payload hash does not match canonical signing payload hash.")
    if not integrity.get("verified"):
        blockers.append("Latest frozen evidence manifest does not match the current evidence bundle.")
    return blockers


def _evidence_row(row: PublicVerifierEvidenceAttachment | None) -> dict:
    if row is None:
        return {}
    return {
        "id": row.id,
        "status": row.verification_status,
        "payload_hash": row.payload_hash,
        "signer_name": row.signer_name,
        "key_reference": row.key_reference,
        "created_at": row.created_at.isoformat() if row.created_at else "",
    }


def _rules() -> list[str]:
    return [
        "Approval requires a Verified public-key evidence record.",
        "Verifier payload hash must match the canonical signing payload hash.",
        "Current bundle must match the latest frozen evidence manifest.",
        "Private keys must remain outside DevFlow Guard.",
    ]


def _markdown(data: dict) -> str:
    lines = ["# v9.6 Verified Evidence Manifest Gate", "", f"Status: {data['status']}", f"Ready: {data['ready']}", "", "## Blockers"]
    lines.extend(f"- {item}" for item in (data["blockers"] or ["No blockers."]))
    lines.extend(["", "## Hardening rules", *[f"- {rule}" for rule in data["hardening_rules"]]])
    return "\n".join(lines).strip() + "\n"
