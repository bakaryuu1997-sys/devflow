from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.database import SessionLocal  # noqa: E402
from app.public_key_verifier_service import public_key_verifier_dry_run  # noqa: E402


def main() -> int:
    out_path = Path(sys.argv[1] if len(sys.argv) > 1 else "PUBLIC_KEY_VERIFIER_DRY_RUN.md")
    with SessionLocal() as db:
        data = public_key_verifier_dry_run(db, {"use_fixture": True})
    out_path.write_text(data["content"], encoding="utf-8")
    print(f"PUBLIC KEY VERIFIER DRY RUN EXPORTED: {out_path}")
    print(f"status={data['status']} verified={data['verified']}")
    return 0 if data.get("verified") else 1


if __name__ == "__main__":
    raise SystemExit(main())
