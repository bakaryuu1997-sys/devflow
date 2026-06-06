from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.database import SessionLocal  # noqa: E402
from app.public_key_verifier_service import public_key_verifier_readiness  # noqa: E402


def main() -> int:
    out_path = Path(sys.argv[1] if len(sys.argv) > 1 else "PUBLIC_KEY_VERIFIER_READINESS.md")
    with SessionLocal() as db:
        data = public_key_verifier_readiness(db)
    out_path.write_text(data["content"], encoding="utf-8")
    print(f"PUBLIC KEY VERIFIER READINESS EXPORTED: {out_path}")
    print(f"status={data['status']}")
    return 0 if data.get("ready") else 1


if __name__ == "__main__":
    raise SystemExit(main())
