from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.final_release_tag_service import RELEASE_TAG, v11_9_final_release_tag_preparation

VERSION = "12.0"
BASELINE_VERSION = "11.9"
BASELINE_ARCHIVE = "devflow_guard_v11_9_final_release_tag_portfolio.zip"
PACKAGE_ARCHIVE = "devflow_guard_v12_0_production_deployment_checklist.zip"
DECISION = "Use v11.9 as portfolio baseline; deploy docs/static first, not full API."


def v12_0_baseline_freeze_summary(db: Session, profile_id: str = "core-risk") -> dict:
    tag = v11_9_final_release_tag_preparation(db, profile_id)
    checks = [
        _check("v11-9-release-tag-ready", tag.get("ready") is True, "Portfolio baseline release tag is ready."),
        _check("release-tag-present", tag.get("release_tag") == RELEASE_TAG, "Release tag is stable."),
        _check("manifest-digest-present", len(tag.get("manifest_digest", "")) == 64, "Evidence digest is available."),
        _check("no-new-feature-scope", True, "v12.0 is checklist and decision only."),
    ]
    data = {
        "version": VERSION,
        "mode": "baseline-freeze-summary",
        "status": "v11.9 baseline freeze confirmed"
        if all(c["pass"] for c in checks)
        else "v11.9 baseline freeze blocked",
        "ready": all(c["pass"] for c in checks),
        "profile_id": profile_id,
        "baseline_version": BASELINE_VERSION,
        "baseline_archive": BASELINE_ARCHIVE,
        "release_tag": RELEASE_TAG,
        "manifest_digest": tag.get("manifest_digest", ""),
        "created_at_utc": _now(),
        "checks": checks,
        "non_goals": _non_goals(),
    }
    data["content"] = _baseline_markdown(data)
    return data


def v12_0_production_deployment_checklist(db: Session, profile_id: str = "core-risk") -> dict:
    freeze = v12_0_baseline_freeze_summary(db, profile_id)
    data = {
        "version": VERSION,
        "mode": "production-deployment-checklist",
        "status": "Deployment checklist ready" if freeze["ready"] else "Deployment checklist blocked",
        "ready": freeze["ready"],
        "profile_id": profile_id,
        "decision": DECISION,
        "hosting_options": _hosting_options(),
        "local_verification": _local_verification_commands(),
        "vercel_static_checklist": _vercel_static_checklist(),
        "api_deployment_checklist": _api_deployment_checklist(),
        "acceptance_gates": _acceptance_gates(),
    }
    data["content"] = _deployment_markdown(data)
    return data


def v12_0_operator_deployment_package(db: Session, profile_id: str = "core-risk") -> dict:
    freeze = v12_0_baseline_freeze_summary(db, profile_id)
    checklist = v12_0_production_deployment_checklist(db, profile_id)
    data = {
        "version": VERSION,
        "mode": "operator-deployment-package",
        "status": "Operator deployment package ready"
        if freeze["ready"] and checklist["ready"]
        else "Operator deployment package blocked",
        "ready": freeze["ready"] and checklist["ready"],
        "profile_id": profile_id,
        "archive_name": PACKAGE_ARCHIVE,
        "baseline_archive": BASELINE_ARCHIVE,
        "release_tag": RELEASE_TAG,
        "decision": DECISION,
    }
    data["content"] = (
        "\n\n".join(
            [
                "# v12.0 Operator Deployment Package",
                freeze["content"],
                checklist["content"],
            ]
        ).strip()
        + "\n"
    )
    return data


def _hosting_options() -> list[dict]:
    return [
        {
            "name": "Local portfolio demo",
            "fit": "best",
            "reason": "Keeps SQLite, FastAPI, and recovery demo behavior intact.",
        },
        {
            "name": "Vercel static/docs",
            "fit": "good",
            "reason": "Good for README, screenshots, quickstart, and portfolio landing page.",
        },
        {
            "name": "Vercel full API",
            "fit": "caution",
            "reason": "Needs serverless refactor and stateless data strategy before relying on it.",
        },
        {
            "name": "FastAPI host",
            "fit": "good",
            "reason": "Best when the interactive API and SQLite demo need to keep working.",
        },
    ]


def _local_verification_commands() -> list[str]:
    return [
        "python -m venv .venv",
        ".venv\\Scripts\\activate",
        "pip install -r requirements.txt",
        "python -m compileall app scripts",
        "pytest tests/test_v119_final_release_tag_portfolio.py",
        "uvicorn app.main:app --reload",
    ]


def _vercel_static_checklist() -> list[str]:
    return [
        "Publish a static portfolio page that links the v11.9 ZIP and quickstart.",
        "Do not promise live API behavior unless a backend host is connected.",
        "Include release tag, manifest digest, and demo script summary.",
        "Keep screenshots or GIFs small enough for fast loading.",
    ]


def _api_deployment_checklist() -> list[str]:
    return [
        "Pick a FastAPI-friendly host before exposing the full API demo.",
        "Set environment variables explicitly and avoid production secrets in ZIP.",
        "Use a disposable demo database, not real user data.",
        "Run smoke test and post-restore verification after deployment.",
    ]


def _acceptance_gates() -> list[str]:
    return [
        "v11.9 runs locally on the user's machine.",
        "Portfolio story can be delivered in under five minutes.",
        "Static page clearly says whether the API is live or local-only.",
        "No new feature work starts before deployment feedback is collected.",
    ]


def _non_goals() -> list[str]:
    return ["No new feature endpoint.", "No destructive reset/restore change.", "No production database migration."]


def _check(check_id: str, passed: bool, detail: str) -> dict:
    return {"id": check_id, "pass": bool(passed), "required": True, "detail": detail}


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _baseline_markdown(data: dict) -> str:
    lines = [
        "# v12.0 Baseline Freeze Summary",
        "",
        f"Status: {data['status']}",
        f"Baseline archive: `{data['baseline_archive']}`",
        f"Release tag: `{data['release_tag']}`",
        f"Manifest digest: `{data['manifest_digest']}`",
        "",
        "## Checks",
    ]
    lines.extend(f"- {'PASS' if item['pass'] else 'BLOCK'}: {item['id']} — {item['detail']}" for item in data["checks"])
    lines.extend(["", "## Non-goals"])
    lines.extend(f"- {item}" for item in data["non_goals"])
    return "\n".join(lines).strip() + "\n"


def _deployment_markdown(data: dict) -> str:
    lines = ["# v12.0 Production Deployment Checklist", "", f"Decision: {data['decision']}", "", "## Hosting Decision"]
    lines.extend(f"- {item['name']} — {item['fit']}: {item['reason']}" for item in data["hosting_options"])
    lines.extend(["", "## Local Verification"])
    lines.extend(f"```bash\n{cmd}\n```" for cmd in data["local_verification"])
    lines.extend(["", "## Vercel Static Checklist"])
    lines.extend(f"- {item}" for item in data["vercel_static_checklist"])
    lines.extend(["", "## Full API Deployment Checklist"])
    lines.extend(f"- {item}" for item in data["api_deployment_checklist"])
    lines.extend(["", "## Acceptance Gates"])
    lines.extend(f"- {item}" for item in data["acceptance_gates"])
    return "\n".join(lines).strip() + "\n"
