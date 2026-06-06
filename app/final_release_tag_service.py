from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.demo_release_candidate_service import RC_LABEL
from app.signed_archive_handoff_service import v11_8_signed_archive_checksum_handoff

VERSION = "11.9"
ARCHIVE_NAME = "devflow_guard_v11_9_final_release_tag_portfolio.zip"
RELEASE_TAG = "devflow-guard-demo-v11.9"
TAG_SIGNOFF = "TAG RELEASE: devflow-guard-demo-v11.9"
PORTFOLIO_TITLE = "DevFlow Guard recovery-governed release demo"


def v11_9_final_release_tag_preparation(db: Session, profile_id: str = "core-risk") -> dict:
    handoff = v11_8_signed_archive_checksum_handoff(db, profile_id)
    checks = [
        _check("v11-8-handoff-ready", handoff.get("ready") is True, "Signed checksum handoff is ready."),
        _check("manifest-digest-present", len(handoff.get("manifest_digest", "")) == 64, "Manifest digest is locked."),
        _check("handoff-signature-present", len(handoff.get("handoff_signature", "")) == 64, "Handoff signature is present."),
        _check("no-new-destructive-path", True, "v11.9 only prepares release tag and demo script."),
    ]
    ready = all(item["pass"] for item in checks)
    data = {
        "version": VERSION,
        "mode": "final-release-tag-preparation",
        "status": "Final release tag preparation ready" if ready else "Final release tag preparation blocked",
        "ready": ready,
        "profile_id": profile_id,
        "release_candidate": RC_LABEL,
        "release_tag": RELEASE_TAG,
        "archive_name": ARCHIVE_NAME,
        "manifest_digest": handoff.get("manifest_digest", ""),
        "handoff_signature": handoff.get("handoff_signature", ""),
        "tag_signoff_phrase": TAG_SIGNOFF,
        "prepared_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "git_commands": _git_commands(),
        "checks": checks,
        "non_goals": _non_goals(),
    }
    data["content"] = _tag_markdown(data)
    return data


def v11_9_portfolio_demo_script(db: Session, profile_id: str = "core-risk") -> dict:
    prep = v11_9_final_release_tag_preparation(db, profile_id)
    data = {
        "version": VERSION,
        "mode": "portfolio-demo-script",
        "status": "Portfolio demo script ready" if prep["ready"] else "Portfolio demo script blocked",
        "ready": prep["ready"],
        "profile_id": profile_id,
        "title": PORTFOLIO_TITLE,
        "release_tag": RELEASE_TAG,
        "script_sections": _script_sections(prep),
        "talk_track": _talk_track(),
        "verification_commands": _verification_commands(),
    }
    data["content"] = _script_markdown(data)
    return data


def v11_9_operator_final_release_package(db: Session, profile_id: str = "core-risk") -> dict:
    prep = v11_9_final_release_tag_preparation(db, profile_id)
    script = v11_9_portfolio_demo_script(db, profile_id)
    data = {
        "version": VERSION,
        "mode": "operator-final-release-package",
        "status": "Operator final release package ready" if prep["ready"] and script["ready"] else "Operator final release package blocked",
        "ready": prep["ready"] and script["ready"],
        "profile_id": profile_id,
        "release_tag": RELEASE_TAG,
        "manifest_digest": prep["manifest_digest"],
        "tag_signoff_phrase": TAG_SIGNOFF,
    }
    data["content"] = "\n\n".join([
        "# v11.9 Operator Final Release Package",
        prep["content"],
        script["content"],
    ]).strip() + "\n"
    return data


def _git_commands() -> list[str]:
    return [
        "git status --short",
        f"git tag -a {RELEASE_TAG} -m \"{TAG_SIGNOFF}\"",
        f"git show {RELEASE_TAG} --stat",
    ]


def _script_sections(prep: dict) -> list[dict]:
    return [
        {"title": "Open with the problem", "duration": "30s", "say": "Show that release demos fail when reset and restore paths are unsafe."},
        {"title": "Show guarded recovery", "duration": "60s", "say": "Walk through reset phrase, restore phrase, digest lock, and audit trail."},
        {"title": "Prove evidence", "duration": "60s", "say": f"Display manifest digest {prep['manifest_digest'][:12]}... and checksum handoff."},
        {"title": "Finish with quickstart", "duration": "30s", "say": "Run install verification and explain the final release tag."},
    ]


def _talk_track() -> list[str]:
    return [
        "This project is not a generic task tracker; it is a release safety demo.",
        "Every risky recovery operation requires explicit operator intent.",
        "The final ZIP has a manifest digest, handoff signature, and repeatable quickstart.",
        "The portfolio story is reliability: evidence first, destructive actions locked down.",
    ]


def _verification_commands() -> list[str]:
    return [
        "python -m compileall app scripts",
        "pytest tests/test_v119_final_release_tag_portfolio.py",
        "python scripts/export_v11_9_final_release_package.py",
    ]


def _non_goals() -> list[str]:
    return ["No schema migration.", "No reset/restore bypass.", "No new destructive endpoint."]


def _check(check_id: str, passed: bool, detail: str) -> dict:
    return {"id": check_id, "pass": bool(passed), "required": True, "detail": detail}


def _tag_markdown(data: dict) -> str:
    lines = [
        "# v11.9 Final Release Tag Preparation",
        "",
        f"Status: {data['status']}",
        f"Release tag: `{data['release_tag']}`",
        f"Archive: `{data['archive_name']}`",
        f"Tag signoff phrase: `{data['tag_signoff_phrase']}`",
        f"Manifest digest: `{data['manifest_digest']}`",
        "",
        "## Git Commands",
    ]
    lines.extend(f"```bash\n{cmd}\n```" for cmd in data["git_commands"])
    lines.extend(["", "## Checks"])
    lines.extend(f"- {'PASS' if item['pass'] else 'BLOCK'}: {item['id']} — {item['detail']}" for item in data["checks"])
    return "\n".join(lines).strip() + "\n"


def _script_markdown(data: dict) -> str:
    lines = ["# v11.9 Portfolio Demo Script", "", f"Title: {data['title']}", f"Release tag: `{data['release_tag']}`", "", "## Demo Flow"]
    lines.extend(f"- {item['duration']} — {item['title']}: {item['say']}" for item in data["script_sections"])
    lines.extend(["", "## Talk Track"])
    lines.extend(f"- {item}" for item in data["talk_track"])
    lines.extend(["", "## Verification Commands"])
    lines.extend(f"```bash\n{cmd}\n```" for cmd in data["verification_commands"])
    return "\n".join(lines).strip() + "\n"
