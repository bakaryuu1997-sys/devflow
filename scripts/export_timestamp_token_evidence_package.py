from __future__ import annotations

import sys
from pathlib import Path

from signature_import_lib import render_token_package, timestamp_token_package


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    out_path = Path(sys.argv[2] if len(sys.argv) > 2 else "TIMESTAMP_TOKEN_EVIDENCE_PACKAGE.md")
    if not db_path.exists():
        print(f"EXPORT FAILED: database not found: {db_path}")
        return 2
    data = timestamp_token_package(db_path)
    out_path.write_text(render_token_package(data), encoding="utf-8")
    print(f"TIMESTAMP TOKEN EVIDENCE PACKAGE EXPORTED: {out_path}")
    print(f"status={data['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
