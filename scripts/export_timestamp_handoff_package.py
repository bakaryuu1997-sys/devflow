from __future__ import annotations

import sys
from pathlib import Path

from signing_readiness_lib import render_timestamp_handoff, timestamp_handoff_package


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    out_path = Path(sys.argv[2] if len(sys.argv) > 2 else "TIMESTAMP_HANDOFF_PACKAGE.md")
    if not db_path.exists():
        print(f"EXPORT FAILED: database not found: {db_path}")
        return 2
    data = timestamp_handoff_package(db_path)
    out_path.write_text(render_timestamp_handoff(data), encoding="utf-8")
    print(f"TIMESTAMP HANDOFF PACKAGE EXPORTED: {out_path}")
    print(f"status={data['status']}")
    print(f"payload_hash={data['payload_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
