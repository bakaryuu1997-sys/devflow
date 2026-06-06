from __future__ import annotations

from sqlalchemy.orm import Session

from app.final_evidence_bundle_service import final_signed_release_bundle_package
from app.release_rehearsal_service import production_upgrade_rehearsal_report
from app.models_v99 import GovernanceRehearsalRecord
from app.verified_gate_hardening_service import verified_evidence_manifest_gate


def end_to_end_governance_rehearsal(db: Session) -> dict:
    migration = production_upgrade_rehearsal_report(db)
    gate = verified_evidence_manifest_gate(db)
    bundle = final_signed_release_bundle_package(db)
    blockers = []
    blockers.extend(migration.get("blockers", []))
    blockers.extend(gate.get("blockers", []))
    if not bundle.get("ready"):
        blockers.append("Final signed evidence bundle is not ready.")
    score = max(0, 100 - len(blockers) * 20)
    data = {
        "version": "9.9",
        "mode": "end-to-end-production-governance-rehearsal",
        "status": "Go" if not blockers else "No-Go",
        "ready": not blockers,
        "readiness_score": score,
        "blockers": blockers,
        "sections": ["migration rehearsal", "verified evidence gate", "final evidence bundle", "operator approval handoff"],
    }
    data["content"] = _markdown(data)
    return data


def record_governance_rehearsal(db: Session, payload: dict) -> dict:
    report = end_to_end_governance_rehearsal(db)
    row = GovernanceRehearsalRecord(
        status=report["status"],
        readiness_score=report["readiness_score"],
        blockers="\n".join(report["blockers"]),
        content=(payload.get("content") or report["content"]).strip(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _row(row)


def list_governance_rehearsals(db: Session) -> dict:
    rows = db.query(GovernanceRehearsalRecord).order_by(GovernanceRehearsalRecord.id.desc()).all()
    data = {"version": "9.9", "mode": "governance-rehearsal-records", "count": len(rows), "records": [_row(row) for row in rows]}
    data["content"] = _list_markdown(data)
    return data


def _row(row: GovernanceRehearsalRecord) -> dict:
    return {"id": row.id, "status": row.status, "readiness_score": row.readiness_score, "blockers": row.blockers.splitlines() if row.blockers else [], "created_at": row.created_at.isoformat() if row.created_at else "", "content": row.content}


def _markdown(data: dict) -> str:
    lines = ["# v9.9 End-to-End Production Release Governance Rehearsal", "", f"Status: {data['status']}", f"Readiness score: {data['readiness_score']}", "", "## Sections"]
    lines.extend(f"- {item}" for item in data["sections"])
    lines.extend(["", "## Blockers"])
    lines.extend(f"- {item}" for item in (data["blockers"] or ["No blockers."]))
    return "\n".join(lines).strip() + "\n"


def _list_markdown(data: dict) -> str:
    lines = ["# v9.9 Governance Rehearsal Records", "", f"Count: {data['count']}"]
    lines.extend(f"- #{row['id']} {row['status']} score={row['readiness_score']}" for row in data["records"])
    return "\n".join(lines).strip() + "\n"
