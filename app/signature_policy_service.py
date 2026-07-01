from __future__ import annotations

import re

from sqlalchemy.orm import Session

from app.signature_import_service import signed_payload_timestamp_integrity_check

HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
ADAPTERS = {
    "generic-sha256-reference": "Hash/reference verification only; no vendor crypto parser.",
    "x509-cms-stub": "Placeholder for X.509/CMS verification adapter.",
    "pgp-stub": "Placeholder for PGP detached signature verification adapter.",
    "rfc3161-tsa-stub": "Placeholder for RFC3161 timestamp token verification adapter.",
    "ed25519-public-key": "First real optional public-key verifier adapter boundary.",
}


def signature_verification_adapter_stubs(db: Session) -> dict:
    integrity = signed_payload_timestamp_integrity_check(db)
    rows = [_adapter_row(name, description, integrity) for name, description in ADAPTERS.items()]
    data = {
        "version": "9.2",
        "mode": "signature-verification-adapter-stubs",
        "status": "Adapter Stubs Ready",
        "payload_hash": integrity.get("current_payload_hash", ""),
        "adapters": rows,
        "rules": _adapter_rules(),
    }
    data["content"] = _adapters_markdown(data)
    return data


def policy_based_verification_checklist(db: Session) -> dict:
    integrity = signed_payload_timestamp_integrity_check(db)
    blockers = _policy_blockers(integrity)
    data = {
        "version": "9.2",
        "mode": "policy-based-verification-checklist",
        "status": "Policy Ready" if not blockers else "Policy Review Needed",
        "ready": not blockers,
        "payload_hash": integrity.get("current_payload_hash", ""),
        "blockers": blockers,
        "checklist": _policy_checklist(blockers),
        "supported_adapters": list(ADAPTERS.keys()),
    }
    data["content"] = _policy_markdown(data)
    return data


def signature_adapter_dry_run(db: Session, payload: dict) -> dict:
    policy = policy_based_verification_checklist(db)
    adapter = (payload.get("adapter") or "generic-sha256-reference").strip()
    payload_hash = (payload.get("payload_hash") or "").strip()
    signature_hash = (payload.get("signature_hash") or "").strip()
    token_hash = (payload.get("token_hash") or "").strip()
    findings = _dry_run_findings(policy, adapter, payload_hash, signature_hash, token_hash)
    data = {
        "version": "9.2",
        "mode": "signature-adapter-dry-run",
        "status": "Dry Run Passed" if not findings else "Dry Run Needs Review",
        "passed": not findings,
        "adapter": adapter,
        "payload_hash": payload_hash,
        "signature_hash_present": bool(signature_hash),
        "timestamp_token_hash_present": bool(token_hash),
        "findings": findings,
        "next_steps": _dry_run_next_steps(findings),
    }
    data["content"] = _dry_run_markdown(data)
    return data


def _adapter_row(name: str, description: str, integrity: dict) -> dict:
    return {
        "name": name,
        "status": "Stub Only",
        "description": description,
        "private_key_storage": "not-supported",
        "network_calls": "not-supported",
        "payload_hash": integrity.get("current_payload_hash", ""),
    }


def _adapter_rules() -> list[str]:
    return [
        "Adapters must not store private keys in DevFlow Guard.",
        "Adapters must verify against the canonical payload hash.",
        "Vendor-specific parsing must be isolated behind a small adapter boundary.",
        "Verification output must include status, algorithm, signer reference, and evidence hash.",
    ]


def _policy_blockers(integrity: dict) -> list[str]:
    blockers = []
    if not integrity.get("signed_payload_verified"):
        blockers.append("No verified signed payload evidence is attached to the current payload.")
    if not integrity.get("timestamp_token_verified"):
        blockers.append("No verified timestamp token evidence is attached to the current payload.")
    return blockers


def _policy_checklist(blockers: list[str]) -> list[dict]:
    base = [
        ("canonical-payload", "Canonical payload hash is frozen and reviewed."),
        ("signature-evidence", "Signed payload evidence is attached and linked to the payload hash."),
        ("timestamp-evidence", "Timestamp token evidence is attached and linked to the payload hash."),
        ("public-verifier", "Verifier/certificate/public key reference is documented outside private key storage."),
        ("operator-approval", "Operator confirms adapter policy before production use."),
    ]
    return [{"id": key, "title": title, "status": "Needs Review" if blockers else "Ready"} for key, title in base]


def _dry_run_findings(policy: dict, adapter: str, payload_hash: str, signature_hash: str, token_hash: str) -> list[str]:
    findings = []
    if adapter not in ADAPTERS:
        findings.append(f"Unknown adapter: {adapter}")
    if payload_hash != policy.get("payload_hash"):
        findings.append("Payload hash does not match the current policy payload hash.")
    if signature_hash and not HEX64.match(signature_hash):
        findings.append("Signature hash is not a SHA-256 style 64-character hex value.")
    if token_hash and not HEX64.match(token_hash):
        findings.append("Timestamp token hash is not a SHA-256 style 64-character hex value.")
    findings.extend(policy.get("blockers", []))
    return findings


def _dry_run_next_steps(findings: list[str]) -> list[str]:
    if findings:
        return ["Resolve findings before enabling a real vendor adapter.", "Re-run signed payload + timestamp integrity check.", "Repeat adapter dry-run with the exact production policy."]
    return ["Keep this adapter in stub mode until vendor parser is selected.", "Document public verifier reference.", "Run production rehearsal before real migration or release approval."]


def _adapters_markdown(data: dict) -> str:
    lines = ["# v9.2 Signature Verification Adapter Stubs", "", f"Payload hash: `{data['payload_hash']}`", "", "## Adapters"]
    lines.extend(f"- {row['name']}: {row['description']}" for row in data["adapters"])
    lines.extend(["", "## Rules", *[f"- {rule}" for rule in data["rules"]]])
    return "\n".join(lines).strip() + "\n"


def _policy_markdown(data: dict) -> str:
    lines = ["# v9.2 Policy-Based Verification Checklist", "", f"Status: {data['status']}", f"Payload hash: `{data['payload_hash']}`", "", "## Checklist"]
    lines.extend(f"- [{item['status']}] {item['title']}" for item in data["checklist"])
    lines.extend(["", "## Blockers", *[f"- {item}" for item in (data["blockers"] or ["No blockers."]) ]])
    return "\n".join(lines).strip() + "\n"


def _dry_run_markdown(data: dict) -> str:
    lines = ["# v9.2 Signature Adapter Dry Run", "", f"Status: {data['status']}", f"Adapter: {data['adapter']}", f"Payload hash: `{data['payload_hash']}`", "", "## Findings"]
    lines.extend(f"- {item}" for item in (data["findings"] or ["No findings."]))
    lines.extend(["", "## Next steps", *[f"- {step}" for step in data["next_steps"]]])
    return "\n".join(lines).strip() + "\n"
