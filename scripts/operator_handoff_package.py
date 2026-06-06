from __future__ import annotations

import sys
from pathlib import Path

from export_upgrade_runbook import build_runbook
from production_upgrade_checklist import APPROVAL_PHRASE, checklist

PACKAGE_FILES = {
    "RUNBOOK.md": "runbook",
    "OPERATOR_HANDOFF.md": "handoff",
    "UPGRADE_COMMANDS.md": "commands",
    "ROLLBACK_DRILL.md": "rollback",
    "POST_MIGRATION_VERIFY.md": "verify",
    "MANIFEST.md": "manifest",
}


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("operator_handoff_v8_6")
    if not db_path.exists():
        print(f"HANDOFF BLOCKED: database not found: {db_path}")
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)
    write_package(db_path, out_dir)
    print(f"OPERATOR HANDOFF PACKAGE EXPORTED: {out_dir}")
    for filename in PACKAGE_FILES:
        print(f"- {out_dir / filename}")
    return 0


def write_package(db_path: Path, out_dir: Path) -> None:
    content_map = {
        "RUNBOOK.md": build_runbook(db_path),
        "OPERATOR_HANDOFF.md": handoff_doc(db_path),
        "UPGRADE_COMMANDS.md": commands_doc(db_path),
        "ROLLBACK_DRILL.md": rollback_doc(db_path),
        "POST_MIGRATION_VERIFY.md": verify_doc(db_path),
        "MANIFEST.md": manifest_doc(db_path),
    }
    for filename, content in content_map.items():
        (out_dir / filename).write_text(content, encoding="utf-8")


def handoff_doc(db_path: Path) -> str:
    return f"""# v8.6 operator handoff

Objective: run a controlled local SQLite production upgrade.

Database: {db_path}
Approval phrase: `{APPROVAL_PHRASE}`

Rules:
- Do not run the real migration before backup, copy migration, and rollback drill pass.
- Keep the app stopped while applying migration to the production database.
- Preserve generated backup files until the app passes smoke testing.
"""


def commands_doc(db_path: Path) -> str:
    lines = ["# v8.6 upgrade commands", ""]
    lines.extend(f"```bash\n{item}\n```" for item in checklist(db_path))
    return "\n".join(lines).strip() + "\n"


def rollback_doc(db_path: Path) -> str:
    return f"""# v8.6 rollback drill

```bash
python scripts/rollback_drill.py {db_path}
```

Success criteria: command prints `ROLLBACK DRILL PASSED` and database checksum is unchanged.
"""


def verify_doc(db_path: Path) -> str:
    return f"""# v8.6 post-migration verification

```bash
python scripts/post_migration_verify.py {db_path}
python scripts/migration_check.py {db_path}
```

Expected result: schema is verified and no migration SQL remains pending.
"""


def manifest_doc(db_path: Path) -> str:
    lines = ["# v8.6 handoff manifest", "", f"Database: {db_path}", f"Approval phrase: {APPROVAL_PHRASE}", "", "## Files"]
    lines.extend(f"- {filename}: {purpose}" for filename, purpose in PACKAGE_FILES.items())
    return "\n".join(lines).strip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
