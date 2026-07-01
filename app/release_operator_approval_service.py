from __future__ import annotations

from sqlalchemy.orm import Session

from app.models_v88 import OperatorApprovalRecord, SignedRehearsalArtifact
from app.production_migration_gate_service import APPROVAL_PHRASE
from app.release_rehearsal_service import operator_signoff_checklist, production_upgrade_rehearsal_report


def signed_rehearsal_artifact_package(db: Session) -> dict:
    rehearsal = production_upgrade_rehearsal_report(db)
    signoff = operator_signoff_checklist(db)
    data = {
        "version": "8.8",
        "mode": "signed-rehearsal-artifact-package",
        "status": "Ready to Sign" if signoff["status"] == "Ready for Signature" else "Blocked",
        "required_signature_text": "I ran and reviewed the production upgrade rehearsal on a copied database.",
        "rehearsal_status": rehearsal["status"],
        "operator_signoff_status": signoff["status"],
        "stored_artifact_count": db.query(SignedRehearsalArtifact).count(),
        "approval_record_count": db.query(OperatorApprovalRecord).count(),
        "rehearsal_report": rehearsal,
        "operator_signoff": signoff,
    }
    data["content"] = _package_markdown(data)
    return data


def create_signed_rehearsal_artifact(db: Session, payload: dict) -> dict:
    package = signed_rehearsal_artifact_package(db)
    signature = (payload.get("signature_text") or "").strip()
    required = package["required_signature_text"]
    status = "Signed" if package["status"] == "Ready to Sign" and signature == required else "Blocked"
    content = _signed_artifact_markdown(package, payload, status)
    artifact = SignedRehearsalArtifact(
        artifact_type="production-upgrade-rehearsal",
        operator_name=(payload.get("operator_name") or "").strip(),
        reviewer_name=(payload.get("reviewer_name") or "").strip(),
        signature_text=signature,
        status=status,
        notes=(payload.get("notes") or "").strip(),
        content=content,
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return _artifact_row(artifact)


def list_signed_rehearsal_artifacts(db: Session) -> dict:
    rows = db.query(SignedRehearsalArtifact).order_by(SignedRehearsalArtifact.id.desc()).all()
    data = {
        "version": "8.8",
        "mode": "signed-rehearsal-artifacts",
        "count": len(rows),
        "artifacts": [_artifact_row(row) for row in rows],
    }
    data["content"] = _artifact_list_markdown(data)
    return data


def create_final_operator_approval_record(db: Session, payload: dict) -> dict:
    artifact = _latest_signed_artifact(db)
    phrase = (payload.get("approval_phrase") or "").strip()
    if not artifact:
        return _blocked_approval("No signed rehearsal artifact is available.")
    if phrase != APPROVAL_PHRASE:
        return _blocked_approval("Approval phrase did not match the required production migration phrase.")
    content = _approval_markdown(artifact, payload)
    record = OperatorApprovalRecord(
        signed_artifact_id=artifact.id,
        approver_name=(payload.get("approver_name") or "").strip(),
        approval_phrase=phrase,
        status="Approved",
        approval_note=(payload.get("approval_note") or "").strip(),
        content=content,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _approval_row(record)


def list_final_operator_approval_records(db: Session) -> dict:
    rows = db.query(OperatorApprovalRecord).order_by(OperatorApprovalRecord.id.desc()).all()
    data = {
        "version": "8.8",
        "mode": "final-operator-approval-records",
        "count": len(rows),
        "records": [_approval_row(row) for row in rows],
    }
    data["content"] = _approval_list_markdown(data)
    return data


def _latest_signed_artifact(db: Session) -> SignedRehearsalArtifact | None:
    return (
        db.query(SignedRehearsalArtifact)
        .filter(SignedRehearsalArtifact.status == "Signed")
        .order_by(SignedRehearsalArtifact.id.desc())
        .first()
    )


def _artifact_row(row: SignedRehearsalArtifact) -> dict:
    return {
        "id": row.id,
        "status": row.status,
        "operator_name": row.operator_name,
        "reviewer_name": row.reviewer_name,
        "signature_text": row.signature_text,
        "notes": row.notes,
        "created_at": row.created_at.isoformat(),
        "content": row.content,
    }


def _approval_row(row: OperatorApprovalRecord) -> dict:
    return {
        "id": row.id,
        "status": row.status,
        "signed_artifact_id": row.signed_artifact_id,
        "approver_name": row.approver_name,
        "approval_note": row.approval_note,
        "created_at": row.created_at.isoformat(),
        "content": row.content,
    }


def _blocked_approval(reason: str) -> dict:
    return {
        "version": "8.8",
        "mode": "final-operator-approval-record",
        "status": "Blocked",
        "reason": reason,
        "content": f"# v8.8 Final Operator Approval Record\n\nStatus: Blocked\n\nReason: {reason}\n",
    }


def _package_markdown(data: dict) -> str:
    lines = [
        "# v8.8 Signed Rehearsal Artifact Package",
        "",
        f"Status: {data['status']}",
        f"Required signature: {data['required_signature_text']}",
        "",
        "## Evidence",
        f"- Rehearsal: {data['rehearsal_status']}",
        f"- Operator sign-off: {data['operator_signoff_status']}",
    ]
    return "\n".join(lines).strip() + "\n"


def _signed_artifact_markdown(package: dict, payload: dict, status: str) -> str:
    lines = [
        "# v8.8 Signed Rehearsal Artifact",
        "",
        f"Status: {status}",
        f"Operator: {payload.get('operator_name', '')}",
        f"Reviewer: {payload.get('reviewer_name', '')}",
        f"Signature: {payload.get('signature_text', '')}",
        "",
        "## Notes",
        payload.get("notes", "") or "No notes.",
        "",
        "## Source package",
        package["content"],
    ]
    return "\n".join(lines).strip() + "\n"


def _approval_markdown(artifact: SignedRehearsalArtifact, payload: dict) -> str:
    lines = [
        "# v8.8 Final Operator Approval Record",
        "",
        "Status: Approved",
        f"Signed artifact: {artifact.id}",
        f"Approver: {payload.get('approver_name', '')}",
        f"Approval phrase: {APPROVAL_PHRASE}",
        "",
        "## Approval note",
        payload.get("approval_note", "") or "No note.",
    ]
    return "\n".join(lines).strip() + "\n"


def _artifact_list_markdown(data: dict) -> str:
    lines = ["# v8.8 Signed Rehearsal Artifacts", "", f"Count: {data['count']}"]
    lines.extend(f"- #{row['id']} {row['status']} operator={row['operator_name']}" for row in data["artifacts"])
    return "\n".join(lines).strip() + "\n"


def _approval_list_markdown(data: dict) -> str:
    lines = ["# v8.8 Final Operator Approval Records", "", f"Count: {data['count']}"]
    lines.extend(f"- #{row['id']} {row['status']} approver={row['approver_name']}" for row in data["records"])
    return "\n".join(lines).strip() + "\n"
