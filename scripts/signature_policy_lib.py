from __future__ import annotations

import re
from pathlib import Path

from signature_import_lib import signed_import_package

HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
ADAPTERS = ["generic-sha256-reference", "x509-cms-stub", "pgp-stub", "rfc3161-tsa-stub"]


def policy_checklist(db_path: Path) -> dict:
    package = signed_import_package(db_path)
    ready = package["status"] == "Ready for Signed Payload Import"
    blockers = [] if ready else ["Signed payload import package is blocked."]
    return {
        "version": "9.2",
        "status": "Policy Ready" if ready else "Policy Review Needed",
        "payload_hash": package["payload_hash"],
        "blockers": blockers,
        "adapters": ADAPTERS,
        "checklist": [
            "Confirm canonical payload hash is frozen.",
            "Attach signed payload evidence to the same payload hash.",
            "Attach timestamp token evidence to the same payload hash.",
            "Document vendor adapter and public verifier reference.",
            "Do not store private keys in DevFlow Guard.",
        ],
    }


def adapter_dry_run(db_path: Path, adapter: str, payload_hash: str, signature_hash: str = "") -> dict:
    policy = policy_checklist(db_path)
    findings = []
    if adapter not in ADAPTERS:
        findings.append(f"Unknown adapter: {adapter}")
    if payload_hash != policy["payload_hash"]:
        findings.append("Payload hash does not match policy payload hash.")
    if signature_hash and not HEX64.match(signature_hash):
        findings.append("Signature hash is not a SHA-256 style 64-character hex value.")
    findings.extend(policy["blockers"])
    return {"version": "9.2", "status": "Dry Run Passed" if not findings else "Dry Run Needs Review", "adapter": adapter, "payload_hash": payload_hash, "findings": findings}


def render_policy(data: dict) -> str:
    lines = ["# v9.2 Policy-Based Verification Checklist", "", f"Status: {data['status']}", f"Payload hash: `{data['payload_hash']}`", "", "## Checklist"]
    lines.extend(f"- [ ] {item}" for item in data["checklist"])
    lines.extend(["", "## Adapters", *[f"- {name}" for name in data["adapters"]]])
    lines.extend(["", "## Blockers", *[f"- {item}" for item in (data["blockers"] or ["No blockers."]) ]])
    return "\n".join(lines).strip() + "\n"


def render_dry_run(data: dict) -> str:
    lines = ["# v9.2 Signature Adapter Dry Run", "", f"Status: {data['status']}", f"Adapter: {data['adapter']}", f"Payload hash: `{data['payload_hash']}`", "", "## Findings"]
    lines.extend(f"- {item}" for item in (data["findings"] or ["No findings."]))
    return "\n".join(lines).strip() + "\n"
