from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.signature_adapter_contract_service import sample_signature_fixtures


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/export_sample_signature_fixtures.py OUTPUT.md")
        return 2
    data = sample_signature_fixtures(None)
    Path(sys.argv[1]).write_text(data["content"], encoding="utf-8")
    print(f"Wrote {sys.argv[1]} ({data['status']})")
    return 0 if not data["blockers"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
