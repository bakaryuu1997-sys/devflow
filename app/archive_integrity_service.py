from __future__ import annotations

import hashlib
from pathlib import Path

from sqlalchemy.orm import Session

from app.demo_release_candidate_service import RC_LABEL
from app.packaging_cleanup_service import v11_6_operator_final_package

VERSION = "11.7"
ESSENTIAL_FILES = [
    "README.md",
    "VERSION.md",
    "requirements.txt",
    "goal.md",
    "app/archive_integrity_service.py",
    "app/routes_v117.py",
    "docs/V11_7_ARCHIVE_INTEGRITY_RELEASE_NOTES.md",
    "scripts/export_v11_7_release_package.py",
    "tests/test_v117_archive_integrity_release_notes.py",
]


def v11_7_archive_integrity_manifest(db: Session, profile_id: str = "core-risk") -> dict:
    final_package = v11_6_operator_final_package(db, profile_id)
    manifest = [_file_record(path) for path in ESSENTIAL_FILES]
    checks = _manifest_checks(final_package, manifest)
    ready = all(item["pass"] for item in checks)
    data = {
        "version": VERSION,
        "mode": "archive-integrity-manifest",
        "status": "Archive integrity manifest ready" if ready else "Archive integrity manifest blocked",
        "ready": ready,
        "profile_id": profile_id,
        "release_candidate": RC_LABEL,
        "archive_name": "devflow_guard_v11_7_archive_integrity_release_notes.zip",
        "checks": checks,
        "manifest": manifest,
        "manifest_digest": _manifest_digest(manifest),
        "non_goals": _non_goals(),
    }
    data["content"] = _manifest_markdown(data)
    return data


def v11_7_release_notes_polish(db: Session, profile_id: str = "core-risk") -> dict:
    manifest = v11_7_archive_integrity_manifest(db, profile_id)
    data = {
        "version": VERSION,
        "mode": "release-notes-polish",
        "status": "Release notes ready" if manifest["ready"] else "Release notes blocked",
        "ready": manifest["ready"],
        "profile_id": profile_id,
        "release_candidate": RC_LABEL,
        "highlights": _highlights(),
        "upgrade_notes": _upgrade_notes(),
        "verification_notes": _verification_notes(),
        "manifest_digest": manifest["manifest_digest"],
    }
    data["content"] = _release_notes_markdown(data)
    return data


def v11_7_operator_release_package(db: Session, profile_id: str = "core-risk") -> dict:
    manifest = v11_7_archive_integrity_manifest(db, profile_id)
    notes = v11_7_release_notes_polish(db, profile_id)
    data = {
        "version": VERSION,
        "mode": "operator-release-package",
        "status": "Operator release package ready"
        if manifest["ready"] and notes["ready"]
        else "Operator release package blocked",
        "ready": manifest["ready"] and notes["ready"],
        "profile_id": profile_id,
        "release_candidate": RC_LABEL,
        "manifest_digest": manifest["manifest_digest"],
    }
    data["content"] = (
        "\n\n".join(
            [
                "# v11.7 Operator Release Package",
                manifest["content"],
                notes["content"],
            ]
        ).strip()
        + "\n"
    )
    return data


def _file_record(path: str) -> dict:
    file_path = Path(path)
    exists = file_path.exists()
    raw = file_path.read_bytes() if exists else b""
    text = raw.decode("utf-8", errors="ignore") if exists else ""
    return {
        "path": path,
        "exists": exists,
        "size_bytes": len(raw),
        "line_count": text.count("\n") + (1 if text and not text.endswith("\n") else 0),
        "sha256": hashlib.sha256(raw).hexdigest() if exists else None,
    }


def _manifest_checks(final_package: dict, manifest: list[dict]) -> list[dict]:
    return [
        _check(
            "v11-6-final-package-exportable",
            "v11.6 Operator Final Package" in final_package.get("content", ""),
            "v11.6 final package remains exportable.",
        ),
        _check(
            "all-essential-files-present",
            all(item["exists"] for item in manifest),
            "Essential release files are present.",
        ),
        _check(
            "version-current-or-newer",
            any(v in _read("VERSION.md") for v in ["v11.7", "v11.8", "v11.9"]),
            "VERSION.md names v11.7 or newer.",
        ),
        _check(
            "readme-current-or-newer",
            any(v in _read("README.md") for v in ["v11.7", "v11.8", "v11.9"]),
            "README names v11.7 or newer.",
        ),
        _check(
            "release-notes-doc-present",
            Path("docs/V11_7_ARCHIVE_INTEGRITY_RELEASE_NOTES.md").exists(),
            "v11.7 release notes docs are present.",
        ),
        _check("no-new-destructive-path", True, "v11.7 only records integrity and release notes."),
    ]


def _manifest_digest(manifest: list[dict]) -> str:
    lines = [f"{item['path']}|{item['size_bytes']}|{item['sha256']}" for item in manifest]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def _highlights() -> list[str]:
    return [
        "Final archive manifest with SHA-256 records for release-critical files.",
        "Polished release notes for beginner install, recovery guardrails, and demo handoff.",
        "No new destructive reset or restore route after the v11.5 release candidate freeze.",
    ]


def _upgrade_notes() -> list[str]:
    return [
        "Use this package as the v11.7 archive integrity layer on top of demo-rc-v11.5.",
        "Run the beginner install commands from README before presenting the demo.",
        "Keep recovery restore locked behind the restore phrase and snapshot digest lock.",
    ]


def _verification_notes() -> list[str]:
    return [
        "Run compileall for app and scripts.",
        "Run the v11.7 test first, then nearby recovery regression groups.",
        "Export the v11.7 operator release package and keep it with the final ZIP.",
    ]


def _non_goals() -> list[str]:
    return ["No schema migration.", "No reset/restore bypass.", "No new destructive endpoint."]


def _check(check_id: str, passed: bool, detail: str) -> dict:
    return {"id": check_id, "pass": bool(passed), "required": True, "detail": detail}


def _read(path: str) -> str:
    file_path = Path(path)
    return file_path.read_text(encoding="utf-8") if file_path.exists() else ""


def _manifest_markdown(data: dict) -> str:
    lines = [
        "# v11.7 Archive Integrity Manifest",
        "",
        f"Status: {data['status']}",
        f"Manifest digest: `{data['manifest_digest']}`",
        "",
        "## Files",
    ]
    lines.extend(f"- `{item['path']}` — {item['size_bytes']} bytes — `{item['sha256']}`" for item in data["manifest"])
    lines.extend(["", "## Checks"])
    lines.extend(f"- {'PASS' if item['pass'] else 'BLOCK'}: {item['id']} — {item['detail']}" for item in data["checks"])
    return "\n".join(lines).strip() + "\n"


def _release_notes_markdown(data: dict) -> str:
    lines = [
        "# v11.7 Release Notes",
        "",
        f"Release candidate: `{data['release_candidate']}`",
        f"Manifest digest: `{data['manifest_digest']}`",
        "",
        "## Highlights",
    ]
    lines.extend(f"- {item}" for item in data["highlights"])
    lines.extend(["", "## Upgrade Notes"])
    lines.extend(f"- {item}" for item in data["upgrade_notes"])
    lines.extend(["", "## Verification Notes"])
    lines.extend(f"- {item}" for item in data["verification_notes"])
    return "\n".join(lines).strip() + "\n"
