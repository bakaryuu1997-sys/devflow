from __future__ import annotations


def readiness_markdown(data: dict) -> str:
    lines = [
        "# v9.4 Public-Key Verifier Readiness",
        "",
        f"Status: {data['status']}",
        f"Adapter: `{data['adapter']}`",
        f"Optional dependency available: {data['optional_dependency_available']}",
        "",
        "## Blockers",
    ]
    lines.extend(f"- {item}" for item in (data["blockers"] or ["No blockers."]))
    lines.extend(["", "## Rules", *[f"- {rule}" for rule in data["rules"]]])
    return "\n".join(lines).strip() + "\n"


def fixture_markdown(data: dict) -> str:
    lines = ["# v9.4 Public-Key Verifier Fixture Package", "", f"Status: {data['status']}", "", "## Files"]
    lines.extend(
        f"- {row['name']}: `{row['path']}` sha256=`{row['sha256']}`"
        for row in data["fixture"]["files"]
    )
    lines.extend(["", "## Rules", *[f"- {rule}" for rule in data["rules"]]])
    return "\n".join(lines).strip() + "\n"


def dry_run_markdown(data: dict) -> str:
    lines = [
        "# v9.4 Public-Key Verifier Dry Run",
        "",
        f"Status: {data['status']}",
        f"Verified: {data['verified']}",
        f"Payload hash: `{data['payload_hash']}`",
        f"Signature hash: `{data['signature_hash']}`",
        f"Public key hash: `{data['public_key_hash']}`",
        "",
        "## Findings",
    ]
    lines.extend(f"- {item}" for item in (data["findings"] or ["No findings."]))
    lines.extend(["", "## Next steps", *[f"- {step}" for step in data["next_steps"]]])
    return "\n".join(lines).strip() + "\n"
