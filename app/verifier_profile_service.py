from __future__ import annotations

from sqlalchemy.orm import Session

from app.models_v97 import ExternalVerifierProfile


def policy_presets() -> dict:
    presets = [
        _preset("standard-release", "Standard Release", True, False, False),
        _preset("regulated-release", "Regulated Release", True, True, True),
        _preset("demo-local", "Demo Local", False, False, False),
    ]
    data = {"version": "9.7", "mode": "operator-policy-presets", "count": len(presets), "presets": presets}
    data["content"] = _presets_markdown(data)
    return data


def verifier_profile_registry(db: Session) -> dict:
    rows = db.query(ExternalVerifierProfile).order_by(ExternalVerifierProfile.id.desc()).all()
    profiles = [_row(row) for row in rows] or [_default_profile()]
    data = {"version": "9.7", "mode": "external-verifier-profile-registry", "count": len(profiles), "profiles": profiles}
    data["content"] = _profiles_markdown(data)
    return data


def create_verifier_profile(db: Session, payload: dict) -> dict:
    name = (payload.get("name") or "default-ed25519-operator").strip()
    existing = db.query(ExternalVerifierProfile).filter(ExternalVerifierProfile.name == name).first()
    if existing:
        return _row(existing)
    row = ExternalVerifierProfile(
        name=name,
        adapter=(payload.get("adapter") or "ed25519-public-key").strip(),
        policy_preset=(payload.get("policy_preset") or "standard-release").strip(),
        key_reference=(payload.get("key_reference") or "external-kms-or-public-key-reference").strip(),
        status=(payload.get("status") or "Active").strip(),
        notes=(payload.get("notes") or "Created from v9.7 registry.").strip(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _row(row)


def _preset(key: str, name: str, signature: bool, timestamp: bool, frozen_manifest: bool) -> dict:
    return {"key": key, "name": name, "requires_signature": signature, "requires_timestamp": timestamp, "requires_frozen_manifest_match": frozen_manifest}


def _default_profile() -> dict:
    return {"id": 0, "name": "default-ed25519-operator", "adapter": "ed25519-public-key", "policy_preset": "standard-release", "key_reference": "configure-external-public-key", "status": "Template", "notes": "Create a real profile before production sign-off.", "created_at": ""}


def _row(row: ExternalVerifierProfile) -> dict:
    return {"id": row.id, "name": row.name, "adapter": row.adapter, "policy_preset": row.policy_preset, "key_reference": row.key_reference, "status": row.status, "notes": row.notes, "created_at": row.created_at.isoformat() if row.created_at else ""}


def _profiles_markdown(data: dict) -> str:
    lines = ["# v9.7 External Verifier Profile Registry", "", f"Count: {data['count']}"]
    lines.extend(f"- {row['name']} · {row['adapter']} · {row['policy_preset']} · {row['status']}" for row in data["profiles"])
    return "\n".join(lines).strip() + "\n"


def _presets_markdown(data: dict) -> str:
    lines = ["# v9.7 Operator Policy Presets", ""]
    lines.extend(f"- {row['key']}: signature={row['requires_signature']} timestamp={row['requires_timestamp']} frozen_manifest={row['requires_frozen_manifest_match']}" for row in data["presets"])
    return "\n".join(lines).strip() + "\n"
