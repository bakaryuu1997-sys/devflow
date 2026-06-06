from __future__ import annotations

import sys
from pathlib import Path

from signature_import_lib import render_signed_record, verify_signed_payload


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    payload_hash = sys.argv[2] if len(sys.argv) > 2 else ""
    signature_hash = sys.argv[3] if len(sys.argv) > 3 else ""
    out_path = Path(sys.argv[4] if len(sys.argv) > 4 else "SIGNED_PAYLOAD_VERIFICATION.md")
    if not db_path.exists():
        print(f"VERIFY FAILED: database not found: {db_path}")
        return 2
    data = verify_signed_payload(db_path, payload_hash, signature_hash)
    out_path.write_text(render_signed_record(data["status"], data["payload_hash"]), encoding="utf-8")
    print(f"SIGNED PAYLOAD IMPORT VERIFIED: {out_path}")
    print(f"status={data['status']}")
    return 0 if data["status"] == "Verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
