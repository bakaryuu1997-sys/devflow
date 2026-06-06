from __future__ import annotations

import sys
from pathlib import Path

from signature_policy_lib import policy_checklist, render_policy


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    out_path = Path(sys.argv[2] if len(sys.argv) > 2 else "SIGNATURE_POLICY_CHECKLIST.md")
    if not db_path.exists():
        print(f"EXPORT FAILED: database not found: {db_path}")
        return 2
    data = policy_checklist(db_path)
    out_path.write_text(render_policy(data), encoding="utf-8")
    print(f"SIGNATURE POLICY CHECKLIST EXPORTED: {out_path}")
    print(f"status={data['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
