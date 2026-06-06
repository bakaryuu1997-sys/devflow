from __future__ import annotations

import sys
from pathlib import Path

from evidence_manifest_lib import build_manifest, render_manifest


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    out_path = Path(sys.argv[2] if len(sys.argv) > 2 else "EVIDENCE_MANIFEST.md")
    if not db_path.exists():
        print(f"EXPORT FAILED: database not found: {db_path}")
        return 2
    data = build_manifest(db_path)
    out_path.write_text(render_manifest(data), encoding="utf-8")
    print(f"EVIDENCE MANIFEST EXPORTED: {out_path}")
    print(f"manifest_hash={data['manifest_hash']}")
    print(f"bundle_hash={data['bundle_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
