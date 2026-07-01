from __future__ import annotations

import hashlib

from sqlalchemy.orm import Session

from app.evidence_manifest_service import current_evidence_manifest
from app.models_v95 import PublicVerifierEvidenceAttachment
from app.models_v98 import FinalSignedEvidenceBundle
from app.verified_gate_hardening_service import verified_evidence_manifest_gate
from app.verifier_profile_service import verifier_profile_registry


def final_signed_release_bundle_package(db: Session) -> dict:
    gate = verified_evidence_manifest_gate(db)
    manifest = current_evidence_manifest(db)
    profile = _active_profile(db)
    bundle_hash = _bundle_hash(manifest, profile)
    data = {
        "version": "9.8",
        "mode": "final-signed-release-evidence-bundle",
        "status": "Ready to Export" if gate["ready"] else "Blocked",
        "ready": gate["ready"],
        "manifest_hash": manifest.get("manifest_hash", ""),
        "bundle_hash": bundle_hash,
        "profile": profile,
        "gate": gate,
        "export_files": _export_files(),
    }
    data["content"] = _markdown(data)
    return data


def create_final_signed_release_bundle(db: Session, payload: dict) -> dict:
    package = final_signed_release_bundle_package(db)
    latest = db.query(PublicVerifierEvidenceAttachment).order_by(PublicVerifierEvidenceAttachment.id.desc()).first()
    row = FinalSignedEvidenceBundle(
        manifest_hash=package["manifest_hash"],
        bundle_hash=package["bundle_hash"],
        verifier_evidence_id=latest.id if latest else 0,
        profile_name=package["profile"].get("name", ""),
        status="Final" if package["ready"] else "Blocked",
        content=package["content"],
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _row(row)


def list_final_signed_release_bundles(db: Session) -> dict:
    rows = db.query(FinalSignedEvidenceBundle).order_by(FinalSignedEvidenceBundle.id.desc()).all()
    data = {
        "version": "9.8",
        "mode": "final-signed-release-evidence-bundles",
        "count": len(rows),
        "bundles": [_row(row) for row in rows],
    }
    data["content"] = _list_markdown(data)
    return data


def _active_profile(db: Session) -> dict:
    profiles = verifier_profile_registry(db)["profiles"]
    return next((p for p in profiles if p.get("status") == "Active"), profiles[0])


def _bundle_hash(manifest: dict, profile: dict) -> str:
    source = f"{manifest.get('manifest_hash', '')}|{manifest.get('bundle_hash', '')}|{profile.get('name', '')}|{profile.get('key_reference', '')}"
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _export_files() -> list[str]:
    return [
        "FINAL_EVIDENCE_BUNDLE.md",
        "EVIDENCE_MANIFEST.md",
        "VERIFIED_SIGNATURE_GATE.md",
        "OPERATOR_APPROVAL_RECORD.md",
    ]


def _row(row: FinalSignedEvidenceBundle) -> dict:
    return {
        "id": row.id,
        "status": row.status,
        "manifest_hash": row.manifest_hash,
        "bundle_hash": row.bundle_hash,
        "verifier_evidence_id": row.verifier_evidence_id,
        "profile_name": row.profile_name,
        "created_at": row.created_at.isoformat() if row.created_at else "",
        "content": row.content,
    }


def _markdown(data: dict) -> str:
    lines = [
        "# v9.8 Final Signed Release Evidence Bundle",
        "",
        f"Status: {data['status']}",
        f"Ready: {data['ready']}",
        f"Manifest hash: `{data['manifest_hash']}`",
        f"Bundle hash: `{data['bundle_hash']}`",
        "",
        "## Export files",
    ]
    lines.extend(f"- {item}" for item in data["export_files"])
    return "\n".join(lines).strip() + "\n"


def _list_markdown(data: dict) -> str:
    lines = ["# v9.8 Final Signed Release Evidence Bundles", "", f"Count: {data['count']}"]
    lines.extend(f"- #{row['id']} {row['status']} · {row['bundle_hash']}" for row in data["bundles"])
    return "\n".join(lines).strip() + "\n"
