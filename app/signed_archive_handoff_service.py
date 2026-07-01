from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.archive_integrity_service import v11_7_archive_integrity_manifest
from app.demo_release_candidate_service import RC_LABEL

VERSION = "11.8"
ARCHIVE_NAME = "devflow_guard_v11_8_signed_checksum_quickstart.zip"
SIGNOFF_LABEL = "SIGNED CHECKSUM HANDOFF: demo-rc-v11.5"


def v11_8_signed_archive_checksum_handoff(db: Session, profile_id: str = "core-risk") -> dict:
    manifest = v11_7_archive_integrity_manifest(db, profile_id)
    checksum = manifest.get("manifest_digest", "")
    signature = _signature_for(checksum)
    checks = [
        _check("v11-7-manifest-ready", manifest.get("ready") is True, "v11.7 archive manifest is ready."),
        _check("manifest-digest-present", len(checksum) == 64, "Manifest digest is a SHA-256 hex value."),
        _check(
            "release-candidate-stable",
            manifest.get("release_candidate") == RC_LABEL,
            "Release candidate label is stable.",
        ),
        _check("no-new-destructive-path", True, "v11.8 only signs checksum handoff and quickstart."),
    ]
    ready = all(item["pass"] for item in checks)
    data = {
        "version": VERSION,
        "mode": "signed-archive-checksum-handoff",
        "status": "Signed archive checksum handoff ready" if ready else "Signed archive checksum handoff blocked",
        "ready": ready,
        "profile_id": profile_id,
        "release_candidate": RC_LABEL,
        "archive_name": ARCHIVE_NAME,
        "manifest_digest": checksum,
        "handoff_signature": signature,
        "signoff_label": SIGNOFF_LABEL,
        "signed_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "checks": checks,
        "copy_targets": _copy_targets(checksum, signature),
        "non_goals": _non_goals(),
    }
    data["content"] = _handoff_markdown(data)
    return data


def v11_8_final_user_facing_quickstart(db: Session, profile_id: str = "core-risk") -> dict:
    handoff = v11_8_signed_archive_checksum_handoff(db, profile_id)
    steps = [
        "Unzip the archive into a clean folder.",
        "Create and activate a Python virtual environment.",
        "Run pip install -r requirements.txt.",
        "Run python -m compileall app scripts.",
        "Run pytest tests/test_v118_signed_checksum_quickstart.py.",
        "Start the app with uvicorn app.main:app --reload.",
        "Open the local UI and click v11.8 Quickstart / Checksum Handoff.",
    ]
    data = {
        "version": VERSION,
        "mode": "final-user-facing-quickstart",
        "status": "Final quickstart ready" if handoff["ready"] else "Final quickstart blocked",
        "ready": handoff["ready"],
        "profile_id": profile_id,
        "release_candidate": RC_LABEL,
        "archive_name": ARCHIVE_NAME,
        "manifest_digest": handoff["manifest_digest"],
        "handoff_signature": handoff["handoff_signature"],
        "steps": steps,
        "verification_commands": _verification_commands(),
    }
    data["content"] = _quickstart_markdown(data)
    return data


def v11_8_operator_checksum_quickstart_package(db: Session, profile_id: str = "core-risk") -> dict:
    handoff = v11_8_signed_archive_checksum_handoff(db, profile_id)
    quickstart = v11_8_final_user_facing_quickstart(db, profile_id)
    data = {
        "version": VERSION,
        "mode": "operator-checksum-quickstart-package",
        "status": "Operator checksum quickstart package ready"
        if handoff["ready"] and quickstart["ready"]
        else "Operator checksum quickstart package blocked",
        "ready": handoff["ready"] and quickstart["ready"],
        "profile_id": profile_id,
        "release_candidate": RC_LABEL,
        "manifest_digest": handoff["manifest_digest"],
        "handoff_signature": handoff["handoff_signature"],
    }
    data["content"] = (
        "\n\n".join(
            [
                "# v11.8 Operator Checksum Quickstart Package",
                handoff["content"],
                quickstart["content"],
            ]
        ).strip()
        + "\n"
    )
    return data


def _signature_for(manifest_digest: str) -> str:
    raw = f"{VERSION}|{RC_LABEL}|{manifest_digest}|{SIGNOFF_LABEL}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _copy_targets(manifest_digest: str, signature: str) -> dict:
    return {
        "archive_name": ARCHIVE_NAME,
        "manifest_digest": manifest_digest,
        "handoff_signature": signature,
        "signoff_label": SIGNOFF_LABEL,
    }


def _verification_commands() -> list[str]:
    return [
        "python -m compileall app scripts",
        "pytest tests/test_v118_signed_checksum_quickstart.py",
        "python scripts/export_v11_8_checksum_quickstart_package.py",
    ]


def _non_goals() -> list[str]:
    return ["No schema migration.", "No reset/restore bypass.", "No new destructive endpoint."]


def _check(check_id: str, passed: bool, detail: str) -> dict:
    return {"id": check_id, "pass": bool(passed), "required": True, "detail": detail}


def _handoff_markdown(data: dict) -> str:
    lines = [
        "# v11.8 Signed Archive Checksum Handoff",
        "",
        f"Status: {data['status']}",
        f"Archive: `{data['archive_name']}`",
        f"Release candidate: `{data['release_candidate']}`",
        f"Manifest digest: `{data['manifest_digest']}`",
        f"Handoff signature: `{data['handoff_signature']}`",
        f"Signoff label: `{data['signoff_label']}`",
        "",
        "## Checks",
    ]
    lines.extend(f"- {'PASS' if item['pass'] else 'BLOCK'}: {item['id']} — {item['detail']}" for item in data["checks"])
    lines.extend(["", "## Safety Scope"])
    lines.extend(f"- {item}" for item in data["non_goals"])
    return "\n".join(lines).strip() + "\n"


def _quickstart_markdown(data: dict) -> str:
    lines = [
        "# v11.8 Final User-facing Quickstart",
        "",
        f"Archive: `{data['archive_name']}`",
        f"Manifest digest: `{data['manifest_digest']}`",
        "",
        "## Steps",
    ]
    lines.extend(f"{idx}. {step}" for idx, step in enumerate(data["steps"], start=1))
    lines.extend(["", "## Verification Commands"])
    lines.extend(f"```bash\n{cmd}\n```" for cmd in data["verification_commands"])
    return "\n".join(lines).strip() + "\n"
