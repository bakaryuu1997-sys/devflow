from __future__ import annotations

import hashlib
import json
from typing import Any

from sqlalchemy.orm import Session

from app.models_v88 import OperatorApprovalRecord, SignedRehearsalArtifact
from app.models_v89 import EvidenceManifestRecord
from app.models_v95 import PublicVerifierEvidenceAttachment


def current_evidence_manifest(db: Session) -> dict:
    artifacts = db.query(SignedRehearsalArtifact).order_by(SignedRehearsalArtifact.id.asc()).all()
    approvals = db.query(OperatorApprovalRecord).order_by(OperatorApprovalRecord.id.asc()).all()
    verifier = db.query(PublicVerifierEvidenceAttachment).order_by(PublicVerifierEvidenceAttachment.id.asc()).all()
    items = [_artifact_item(row) for row in artifacts] + [_approval_item(row) for row in approvals] + [_verifier_item(row) for row in verifier]
    manifest_hash = _hash_json({"items": items})
    bundle_hash = _hash_text(_bundle_source(items, manifest_hash))
    data = {
        "version": "8.9",
        "mode": "evidence-manifest",
        "algorithm": "sha256",
        "status": "Ready" if items else "No Evidence",
        "immutable": False,
        "item_count": len(items),
        "artifact_count": len(artifacts),
        "approval_count": len(approvals),
        "verifier_evidence_count": len(verifier),
        "manifest_hash": manifest_hash,
        "bundle_hash": bundle_hash,
        "items": items,
        "latest_frozen_manifest": _latest_frozen_hash(db),
    }
    data["content"] = _manifest_markdown(data)
    return data


def freeze_evidence_manifest(db: Session, payload: dict) -> dict:
    manifest = current_evidence_manifest(db)
    record = EvidenceManifestRecord(
        algorithm=manifest["algorithm"],
        manifest_hash=manifest["manifest_hash"],
        bundle_hash=manifest["bundle_hash"],
        status="Frozen" if manifest["item_count"] else "Empty",
        artifact_count=manifest["artifact_count"],
        approval_count=manifest["approval_count"],
        item_count=manifest["item_count"],
        notes=(payload.get("notes") or "").strip(),
        content=manifest["content"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _record_row(record)


def list_evidence_manifests(db: Session) -> dict:
    rows = db.query(EvidenceManifestRecord).order_by(EvidenceManifestRecord.id.desc()).all()
    data = {"version": "8.9", "mode": "evidence-manifests", "count": len(rows), "manifests": [_record_row(row) for row in rows]}
    data["content"] = _manifest_list_markdown(data)
    return data


def export_bundle_integrity_check(db: Session) -> dict:
    current = current_evidence_manifest(db)
    latest = db.query(EvidenceManifestRecord).order_by(EvidenceManifestRecord.id.desc()).first()
    if not latest:
        status = "No Frozen Manifest"
        match = False
        reason = "Freeze an evidence manifest before claiming bundle integrity."
    else:
        match = latest.manifest_hash == current["manifest_hash"] and latest.bundle_hash == current["bundle_hash"]
        status = "Verified" if match else "Changed Since Freeze"
        reason = "Current evidence matches latest frozen manifest." if match else "Evidence changed after the latest frozen manifest."
    data = {
        "version": "8.9",
        "mode": "export-bundle-integrity-check",
        "status": status,
        "verified": match,
        "reason": reason,
        "current_manifest_hash": current["manifest_hash"],
        "current_bundle_hash": current["bundle_hash"],
        "frozen_manifest_hash": latest.manifest_hash if latest else "",
        "frozen_bundle_hash": latest.bundle_hash if latest else "",
        "current": current,
    }
    data["content"] = _integrity_markdown(data)
    return data


def _artifact_item(row: SignedRehearsalArtifact) -> dict:
    return _item("signed_rehearsal_artifacts", row.id, {
        "artifact_type": row.artifact_type,
        "operator_name": row.operator_name,
        "reviewer_name": row.reviewer_name,
        "status": row.status,
        "notes": row.notes,
        "content": row.content,
        "created_at": row.created_at.isoformat(),
    })


def _approval_item(row: OperatorApprovalRecord) -> dict:
    return _item("operator_approval_records", row.id, {
        "signed_artifact_id": row.signed_artifact_id,
        "approver_name": row.approver_name,
        "status": row.status,
        "approval_note": row.approval_note,
        "content": row.content,
        "created_at": row.created_at.isoformat(),
    })


def _verifier_item(row: PublicVerifierEvidenceAttachment) -> dict:
    return _item("public_verifier_evidence_attachments", row.id, {
        "adapter": row.adapter,
        "payload_hash": row.payload_hash,
        "signature_hash": row.signature_hash,
        "public_key_hash": row.public_key_hash,
        "verification_status": row.verification_status,
        "signer_name": row.signer_name,
        "created_at": row.created_at.isoformat(),
    })


def _item(table: str, row_id: int, payload: dict[str, Any]) -> dict:
    record_hash = _hash_json(payload)
    return {"table": table, "id": row_id, "record_hash": record_hash, "status": payload.get("status", ""), "created_at": payload.get("created_at", "")}


def _latest_frozen_hash(db: Session) -> str:
    row = db.query(EvidenceManifestRecord).order_by(EvidenceManifestRecord.id.desc()).first()
    return row.manifest_hash if row else ""


def _hash_json(value: Any) -> str:
    return _hash_text(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _bundle_source(items: list[dict], manifest_hash: str) -> str:
    rows = [manifest_hash]
    rows.extend(f"{item['table']}:{item['id']}:{item['record_hash']}" for item in items)
    return "\n".join(rows)


def _record_row(row: EvidenceManifestRecord) -> dict:
    return {"id": row.id, "status": row.status, "algorithm": row.algorithm, "manifest_hash": row.manifest_hash, "bundle_hash": row.bundle_hash, "item_count": row.item_count, "artifact_count": row.artifact_count, "approval_count": row.approval_count, "notes": row.notes, "created_at": row.created_at.isoformat(), "content": row.content}


def _manifest_markdown(data: dict) -> str:
    lines = ["# v8.9 Evidence Manifest", "", f"Status: {data['status']}", f"Algorithm: {data['algorithm']}", f"Manifest hash: `{data['manifest_hash']}`", f"Bundle hash: `{data['bundle_hash']}`", "", "## Items"]
    lines.extend(f"- {item['table']}#{item['id']} status={item['status']} hash={item['record_hash']}" for item in data["items"])
    if not data["items"]:
        lines.append("- No signed evidence or approval records yet.")
    return "\n".join(lines).strip() + "\n"


def _manifest_list_markdown(data: dict) -> str:
    lines = ["# v8.9 Frozen Evidence Manifests", "", f"Count: {data['count']}"]
    lines.extend(f"- #{row['id']} {row['status']} items={row['item_count']} manifest={row['manifest_hash']}" for row in data["manifests"])
    return "\n".join(lines).strip() + "\n"


def _integrity_markdown(data: dict) -> str:
    lines = ["# v8.9 Export Bundle Integrity Check", "", f"Status: {data['status']}", f"Verified: {data['verified']}", f"Reason: {data['reason']}", "", "## Hash comparison", f"- Current manifest: `{data['current_manifest_hash']}`", f"- Frozen manifest: `{data['frozen_manifest_hash'] or 'none'}`", f"- Current bundle: `{data['current_bundle_hash']}`", f"- Frozen bundle: `{data['frozen_bundle_hash'] or 'none'}`"]
    return "\n".join(lines).strip() + "\n"
