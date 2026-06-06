from __future__ import annotations

from sqlalchemy.orm import Session

from app.signature_adapter_fixtures import load_fixture_rows
from app.signature_policy_service import ADAPTERS

REQUIRED_RESULT_FIELDS = ["adapter", "status", "payload_hash", "evidence_hash", "findings", "verified"]


def signature_adapter_contract_tests(db: Session) -> dict:
    del db
    fixture_rows = load_fixture_rows()
    cases = [_contract_case(row) for row in fixture_rows]
    blockers = _contract_blockers(cases, fixture_rows)
    data = {
        "version": "9.3",
        "mode": "signature-adapter-contract-tests",
        "status": "Contract Tests Ready" if not blockers else "Contract Tests Need Review",
        "passed": not blockers,
        "required_result_fields": REQUIRED_RESULT_FIELDS,
        "cases": cases,
        "blockers": blockers,
        "notes": [
            "Fixtures are public/sample-only and contain no private keys.",
            "v9.3 validates adapter boundaries, not real PGP/X.509/RFC3161 cryptography.",
        ],
    }
    data["content"] = _contract_markdown(data)
    return data


def sample_signature_fixtures(db: Session) -> dict:
    del db
    rows = load_fixture_rows()
    blockers = [f"Private key marker found in {row['filename']}" for row in rows if row["contains_private_key"]]
    data = {
        "version": "9.3",
        "mode": "sample-signature-fixtures",
        "status": "Fixtures Ready" if not blockers else "Fixture Review Needed",
        "fixture_count": len(rows),
        "fixtures": rows,
        "blockers": blockers,
        "rules": [
            "No fixture may contain private key material.",
            "Fixtures must be safe to commit and share.",
            "Real vendor verification remains outside v9.3 scope.",
        ],
    }
    data["content"] = _fixtures_markdown(data)
    return data


def _contract_case(row: dict) -> dict:
    adapter = row["adapter"]
    supported = adapter in ADAPTERS
    findings = []
    if not supported:
        findings.append("Adapter is not registered in v9.2 policy stubs.")
    if not row["exists"]:
        findings.append("Fixture file is missing.")
    if row["contains_private_key"]:
        findings.append("Fixture contains a private key marker.")
    return {
        "adapter": adapter,
        "fixture": row["filename"],
        "status": "Contract Ready" if not findings else "Needs Review",
        "verified": False,
        "payload_hash": "sample-only-not-production",
        "evidence_hash": row["sha256"],
        "findings": findings,
        "result_shape_ok": not findings,
    }


def _contract_blockers(cases: list[dict], fixtures: list[dict]) -> list[str]:
    blockers = []
    for case in cases:
        if not case["result_shape_ok"]:
            blockers.append(f"{case['adapter']} contract needs review.")
    if len(fixtures) < 3:
        blockers.append("Expected PGP, X.509/CMS, and RFC3161 fixtures.")
    return blockers


def _contract_markdown(data: dict) -> str:
    lines = ["# v9.3 Signature Adapter Contract Tests", "", f"Status: {data['status']}", "", "## Required result fields"]
    lines.extend(f"- `{field}`" for field in data["required_result_fields"])
    lines.extend(["", "## Contract cases"])
    lines.extend(f"- {case['adapter']} / {case['fixture']}: {case['status']}" for case in data["cases"])
    lines.extend(["", "## Blockers"])
    lines.extend(f"- {item}" for item in (data["blockers"] or ["No blockers."]))
    return "\n".join(lines).strip() + "\n"


def _fixtures_markdown(data: dict) -> str:
    lines = ["# v9.3 Sample Signature Fixtures", "", f"Status: {data['status']}", "", "## Fixtures"]
    for row in data["fixtures"]:
        lines.append(f"- {row['adapter']} -> `{row['filename']}` sha256=`{row['sha256']}` private_key={row['contains_private_key']}")
    lines.extend(["", "## Rules"])
    lines.extend(f"- {rule}" for rule in data["rules"])
    return "\n".join(lines).strip() + "\n"
