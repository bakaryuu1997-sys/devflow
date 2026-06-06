from __future__ import annotations

import sys
from pathlib import Path

from dry_run_migration_sql import generate_sql
from production_upgrade_checklist import APPROVAL_PHRASE, checklist


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    if not db_path.exists():
        print(f"RUNBOOK BLOCKED: database not found: {db_path}")
        return 2
    content = build_runbook(db_path)
    if output_path:
        output_path.write_text(content, encoding="utf-8")
        print(f"RUNBOOK EXPORTED: {output_path}")
    else:
        print(content)
    return 0


def build_runbook(db_path: Path) -> str:
    statements = generate_sql(db_path)
    lines = [
        "# v8.6 production upgrade runbook",
        "",
        f"Database: {db_path}",
        f"Pending SQL statements: {len(statements)}",
        f"Approval phrase: {APPROVAL_PHRASE}",
        "",
        "## Operator steps",
    ]
    lines.extend(f"- [ ] {item}" for item in checklist(db_path))
    lines.extend(["", "## SQL preview"])
    lines.append("```sql")
    lines.extend(statements or ["-- No migration SQL pending."])
    lines.append("```")
    return "\n".join(lines).strip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
