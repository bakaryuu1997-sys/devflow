from __future__ import annotations

import sys
from pathlib import Path

from production_upgrade_checklist import APPROVAL_PHRASE


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("OPERATOR_SIGNOFF_CHECKLIST.md")
    if not db_path.exists():
        print(f"SIGNOFF CHECKLIST BLOCKED: database not found: {db_path}")
        return 2
    out_path.write_text(build_signoff_checklist(db_path), encoding="utf-8")
    print(f"OPERATOR SIGNOFF CHECKLIST EXPORTED: {out_path}")
    return 0


def build_signoff_checklist(db_path: Path) -> str:
    return f"""# v8.7 operator sign-off checklist

Database: {db_path}
Production approval phrase: `{APPROVAL_PHRASE}`

## Required sign-offs
- [ ] Operator confirms backup path is recorded.
- [ ] Operator confirms safe-copy migration passed.
- [ ] Operator confirms rollback drill passed.
- [ ] Operator confirms post-migration verification command is ready.
- [ ] Reviewer confirms final production checklist is acceptable.
- [ ] Approver understands real migration requires the exact approval phrase.

## Final gate
Do not run production migration until every checkbox above is complete.
"""


if __name__ == "__main__":
    raise SystemExit(main())
