from __future__ import annotations

import sys
from pathlib import Path

from signature_policy_lib import adapter_dry_run, render_dry_run


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    adapter = sys.argv[2] if len(sys.argv) > 2 else "generic-sha256-reference"
    payload_hash = sys.argv[3] if len(sys.argv) > 3 else ""
    signature_hash = sys.argv[4] if len(sys.argv) > 4 else ""
    out_path = Path(sys.argv[5] if len(sys.argv) > 5 else "SIGNATURE_ADAPTER_DRY_RUN.md")
    if not db_path.exists():
        print(f"DRY RUN FAILED: database not found: {db_path}")
        return 2
    data = adapter_dry_run(db_path, adapter, payload_hash, signature_hash)
    out_path.write_text(render_dry_run(data), encoding="utf-8")
    print(f"SIGNATURE ADAPTER DRY-RUN EXPORTED: {out_path}")
    print(f"status={data['status']}")
    return 0 if data["status"] == "Dry Run Passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
