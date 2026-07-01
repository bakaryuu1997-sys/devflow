from __future__ import annotations

from hashlib import sha256
from typing import Any

from sqlalchemy.orm import Session

from app.public_key_verifier_fixtures import ADAPTER_ID, fixture_metadata, load_fixture_evidence, request_evidence
from app.public_key_verifier_markdown import dry_run_markdown, fixture_markdown, readiness_markdown

try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives import serialization
except Exception:  # pragma: no cover - depends on optional runtime package
    InvalidSignature = None
    serialization = None


def public_key_verifier_readiness(db: Session) -> dict:
    del db
    fixture = fixture_metadata()
    available = _crypto_available()
    blockers = _readiness_blockers(fixture, available)
    data = {
        "version": "9.4",
        "mode": "public-key-verifier-readiness",
        "adapter": ADAPTER_ID,
        "status": "Ready" if not blockers else "Unavailable" if not available else "Needs Review",
        "ready": not blockers,
        "optional_dependency": "cryptography",
        "optional_dependency_available": available,
        "private_key_storage": "not-supported",
        "network_calls": "not-supported",
        "fixture": fixture,
        "blockers": blockers,
        "rules": _rules(),
    }
    data["content"] = readiness_markdown(data)
    return data


def public_key_verifier_fixture_package(db: Session) -> dict:
    del db
    fixture = fixture_metadata()
    blockers = []
    if fixture["contains_private_key_marker"]:
        blockers.append("Fixture contains a private-key marker.")
    if not fixture["all_files_present"]:
        blockers.append("One or more Ed25519 fixture files are missing.")
    data = {
        "version": "9.4",
        "mode": "public-key-verifier-fixture-package",
        "status": "Fixture Ready" if not blockers else "Fixture Review Needed",
        "adapter": ADAPTER_ID,
        "fixture": fixture,
        "blockers": blockers,
        "rules": [
            "Fixture stores payload, public key, and detached signature only.",
            "No private key material may be committed to the app.",
            "Real production verification must use operator-provided public-key material.",
        ],
    }
    data["content"] = fixture_markdown(data)
    return data


def public_key_verifier_dry_run(db: Session, payload: dict[str, Any] | None = None) -> dict:
    del db
    request = payload or {}
    use_fixture = bool(request.get("use_fixture", True))
    adapter = request.get("adapter") or ADAPTER_ID
    fixture = fixture_metadata()
    evidence = load_fixture_evidence() if use_fixture else request_evidence(request)
    findings = _verification_findings(adapter, evidence, fixture)
    verified = False
    status = "Needs Review"
    if not findings:
        verified = _verify_ed25519(evidence)
        status = "Verified" if verified else "Invalid Signature"
        if not verified:
            findings.append("Ed25519 signature verification failed.")
    data = {
        "version": "9.4",
        "mode": "public-key-verifier-dry-run",
        "adapter": adapter,
        "status": status,
        "verified": verified,
        "optional_dependency": "cryptography",
        "optional_dependency_available": _crypto_available(),
        "payload_hash": sha256(evidence["payload_bytes"]).hexdigest() if evidence["payload_bytes"] else "",
        "signature_hash": sha256(evidence["signature_bytes"]).hexdigest() if evidence["signature_bytes"] else "",
        "public_key_hash": sha256(evidence["public_key_pem"].encode()).hexdigest()
        if evidence["public_key_pem"]
        else "",
        "findings": findings,
        "next_steps": _next_steps(verified, findings),
    }
    data["content"] = dry_run_markdown(data)
    return data


def _crypto_available() -> bool:
    return serialization is not None and InvalidSignature is not None


def _verification_findings(adapter: str, evidence: dict, fixture: dict) -> list[str]:
    findings = []
    if adapter != ADAPTER_ID:
        findings.append(f"Unsupported adapter for v9.4 real verifier: {adapter}")
    if not _crypto_available():
        findings.append("Optional dependency cryptography is not installed; verifier is unavailable.")
    if fixture["contains_private_key_marker"]:
        findings.append("Fixture contains a private-key marker.")
    if not evidence["payload_bytes"]:
        findings.append("Payload is missing.")
    if not evidence["public_key_pem"]:
        findings.append("Public key PEM is missing.")
    if not evidence["signature_bytes"]:
        findings.append("Detached signature is missing or not valid base64.")
    return findings


def _verify_ed25519(evidence: dict) -> bool:
    if not _crypto_available():
        return False
    try:
        key = serialization.load_pem_public_key(evidence["public_key_pem"].encode("utf-8"))
        key.verify(evidence["signature_bytes"], evidence["payload_bytes"])
        return True
    except InvalidSignature:
        return False
    except Exception:
        return False


def _contains_private_key_marker(text: str) -> bool:
    upper = text.upper()
    markers = ["BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "BEGIN EC PRIVATE KEY", "PRIVATE KEY-----"]
    return any(marker in upper for marker in markers)


def _readiness_blockers(fixture: dict, available: bool) -> list[str]:
    blockers = []
    if not available:
        blockers.append("Optional dependency cryptography is unavailable.")
    if not fixture["all_files_present"]:
        blockers.append("Sample Ed25519 fixture files are incomplete.")
    if fixture["contains_private_key_marker"]:
        blockers.append("Fixture includes a private-key marker.")
    return blockers


def _rules() -> list[str]:
    return [
        "The app must never store private keys.",
        "The first real verifier accepts public-key material only.",
        "The cryptography package remains optional and isolated behind this adapter boundary.",
        "If the optional dependency is missing, the adapter must return Unavailable instead of crashing.",
    ]


def _next_steps(verified: bool, findings: list[str]) -> list[str]:
    if verified:
        return [
            "Keep production keys outside the app.",
            "Run policy checklist before enabling production verification.",
            "Attach verification output to evidence manifest.",
        ]
    return [
        "Resolve findings.",
        "Re-run with exact payload, public key, and detached signature.",
        "Do not mark production evidence verified until this adapter passes.",
    ]
