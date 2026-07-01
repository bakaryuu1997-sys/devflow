from __future__ import annotations

import sys
from pathlib import Path

from evidence_manifest_lib import build_manifest, latest_frozen_manifest


def main() -> int:
    db_path = Path(sys.argv[1] if len(sys.argv) > 1 else "devflow.db")
    out_path = Path(sys.argv[2] if len(sys.argv) > 2 else "BUNDLE_INTEGRITY_CHECK.md")
    if not db_path.exists():
        print(f"VERIFY FAILED: database not found: {db_path}")
        return 2
    current = build_manifest(db_path)
    frozen = latest_frozen_manifest(db_path)
    verified = bool(
        frozen
        and frozen.get("manifest_hash") == current["manifest_hash"]
        and frozen.get("bundle_hash") == current["bundle_hash"]
    )
    status = "Verified" if verified else "No Frozen Manifest" if not frozen else "Changed Since Freeze"
    lines = [
        "# v8.9 Export Bundle Integrity Check",
        "",
        f"Status: {status}",
        f"Verified: {verified}",
        "",
        "## Hash comparison",
        f"- Current manifest: `{current['manifest_hash']}`",
        f"- Frozen manifest: `{frozen.get('manifest_hash', '') if frozen else 'none'}`",
        f"- Current bundle: `{current['bundle_hash']}`",
        f"- Frozen bundle: `{frozen.get('bundle_hash', '') if frozen else 'none'}`",
    ]
    out_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(f"BUNDLE INTEGRITY CHECK EXPORTED: {out_path}")
    print(f"status={status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
