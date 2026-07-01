from __future__ import annotations

import sys
from pathlib import Path

from migration_check import inspect_database
from production_upgrade_checklist import APPROVAL_PHRASE, checklist


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("REHEARSAL_REPORT.md")
    if not db_path.exists():
        print(f"REHEARSAL BLOCKED: database not found: {db_path}")
        return 2
    out_path.write_text(build_rehearsal_report(db_path), encoding="utf-8")
    print(f"REHEARSAL REPORT EXPORTED: {out_path}")
    return 0


def build_rehearsal_report(db_path: Path) -> str:
    status = inspect_database(db_path)
    commands = checklist(db_path)
    lines = [
        "# v8.7 production upgrade rehearsal report",
        "",
        f"Database: {db_path}",
        f"Approval phrase: `{APPROVAL_PHRASE}`",
        "",
        "## Schema rehearsal status",
    ]
    for item in status:
        mark = "PASS" if not item["missing"] else "MISSING"
        details = ", ".join(item["missing"]) or "none"
        lines.append(f"- {mark}: {item['table']} ({details})")
    lines.extend(["", "## Rehearsal commands"])
    lines.extend(f"```bash\n{command}\n```" for command in commands)
    lines.extend(
        [
            "",
            "## Operator notes",
            "- [ ] Safe copy migration passed",
            "- [ ] Rollback drill passed",
            "- [ ] Post-migration verification command is ready",
        ]
    )
    return "\n".join(lines).strip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
