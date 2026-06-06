from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.demo_release_candidate_service import (
    RC_LABEL,
    v11_5_demo_release_candidate_freeze,
    v11_5_operator_acceptance_checklist,
)

VERSION = "11.6"


def v11_6_final_packaging_cleanup(db: Session, profile_id: str = "core-risk") -> dict:
    freeze = v11_5_demo_release_candidate_freeze(db, profile_id)
    checks = _packaging_checks()
    checks.append(_check("rc-freeze-ready", freeze.get("ready"), "v11.5 RC freeze is still ready."))
    ready = all(item["pass"] for item in checks)
    data = {
        "version": VERSION,
        "mode": "final-packaging-cleanup",
        "status": "Final package cleanup ready" if ready else "Final package cleanup blocked",
        "ready": ready,
        "profile_id": profile_id,
        "release_candidate": RC_LABEL,
        "checks": checks,
        "cleanup_notes": _cleanup_notes(),
        "non_goals": _non_goals(),
    }
    data["content"] = _cleanup_markdown(data)
    return data


def v11_6_beginner_install_verification(db: Session, profile_id: str = "core-risk") -> dict:
    acceptance = v11_5_operator_acceptance_checklist(db, profile_id)
    steps = _install_steps()
    checks = _install_checks()
    checks.append(_check("operator-acceptance-ready", acceptance.get("ready"), "RC acceptance checklist is ready."))
    ready = all(item["pass"] for item in checks)
    data = {
        "version": VERSION,
        "mode": "beginner-install-verification",
        "status": "Beginner install verification ready" if ready else "Beginner install verification blocked",
        "ready": ready,
        "profile_id": profile_id,
        "release_candidate": RC_LABEL,
        "install_steps": steps,
        "checks": checks,
        "verification_commands": _verification_commands(),
    }
    data["content"] = _install_markdown(data)
    return data


def v11_6_operator_final_package(db: Session, profile_id: str = "core-risk") -> dict:
    cleanup = v11_6_final_packaging_cleanup(db, profile_id)
    install = v11_6_beginner_install_verification(db, profile_id)
    data = {
        "version": VERSION,
        "mode": "operator-final-package",
        "status": "Operator final package ready" if cleanup["ready"] and install["ready"] else "Operator final package blocked",
        "ready": cleanup["ready"] and install["ready"],
        "profile_id": profile_id,
        "release_candidate": RC_LABEL,
    }
    data["content"] = "\n\n".join([
        "# v11.6 Operator Final Package",
        cleanup["content"],
        install["content"],
    ]).strip() + "\n"
    return data


def _packaging_checks() -> list[dict]:
    return [
        _check("readme-current-or-newer", any(v in _read("README.md") for v in ["v11.6", "v11.7", "v11.8", "v11.9"]), "README names v11.6 or newer."),
        _check("version-current-or-newer", any(v in _read("VERSION.md") for v in ["v11.6", "v11.7", "v11.8", "v11.9"]), "VERSION.md is current or newer."),
        _check("requirements-present", Path("requirements.txt").exists(), "requirements.txt is present."),
        _check("docs-present", Path("docs/V11_6_FINAL_PACKAGING_INSTALL.md").exists(), "v11.6 docs are present."),
        _check("no-new-destructive-path", True, "v11.6 only packages and verifies installation."),
    ]


def _install_checks() -> list[dict]:
    req = _read("requirements.txt")
    readme = _read("README.md")
    return [
        _check("venv-step-present", "python -m venv .venv" in readme, "README shows virtualenv setup."),
        _check("pip-install-step-present", "pip install -r requirements.txt" in readme, "README shows dependency install."),
        _check("run-step-present", "uvicorn app.main:app --reload" in readme, "README shows local run command."),
        _check("sqlalchemy-dependency", "sqlalchemy" in req, "SQLAlchemy dependency is declared."),
        _check("pytest-dependency", "pytest" in req, "pytest dependency is declared."),
    ]


def _install_steps() -> list[str]:
    return [
        "Create a virtual environment.",
        "Install dependencies from requirements.txt.",
        "Run the FastAPI app with uvicorn.",
        "Open http://localhost:8000 and build the core-risk sample project.",
        "Run the v11.6 final package export script.",
    ]


def _verification_commands() -> list[str]:
    return [
        "python -m venv .venv",
        ".venv\\Scripts\\activate",
        "pip install -r requirements.txt",
        "python -m compileall app scripts",
        "pytest tests/test_v116_final_packaging_install.py",
        "python scripts/export_v11_6_operator_final_package.py",
        "uvicorn app.main:app --reload",
    ]


def _cleanup_notes() -> list[str]:
    return [
        "Keep v11.5 as the release candidate label.",
        "Ship v11.6 as the beginner-friendly final package cleanup layer.",
        "Prefer small verification commands over a huge all-at-once test run.",
    ]


def _non_goals() -> list[str]:
    return [
        "No destructive reset or restore endpoint.",
        "No schema migration.",
        "No bypass around restore phrase or digest lock.",
    ]


def _check(check_id: str, passed: bool, detail: str) -> dict:
    return {"id": check_id, "pass": bool(passed), "required": True, "detail": detail}


def _read(path: str) -> str:
    file_path = Path(path)
    return file_path.read_text(encoding="utf-8") if file_path.exists() else ""


def _cleanup_markdown(data: dict) -> str:
    lines = [
        "# v11.6 Final Packaging Cleanup",
        "",
        f"Status: {data['status']}",
        f"Release candidate: `{data['release_candidate']}`",
        f"Profile: {data['profile_id']}",
        "",
        "## Checks",
    ]
    lines.extend(f"- {'PASS' if item['pass'] else 'BLOCK'}: {item['id']} — {item['detail']}" for item in data["checks"])
    lines.extend(["", "## Cleanup Notes"])
    lines.extend(f"- {item}" for item in data["cleanup_notes"])
    return "\n".join(lines).strip() + "\n"


def _install_markdown(data: dict) -> str:
    lines = [
        "# v11.6 Beginner Install Verification",
        "",
        f"Status: {data['status']}",
        "",
        "## Steps",
    ]
    lines.extend(f"{idx}. {step}" for idx, step in enumerate(data["install_steps"], start=1))
    lines.extend(["", "## Verification Commands"])
    lines.extend(f"- `{cmd}`" for cmd in data["verification_commands"])
    return "\n".join(lines).strip() + "\n"
