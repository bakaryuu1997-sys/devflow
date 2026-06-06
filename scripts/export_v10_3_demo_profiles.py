from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.tutorial_mode_service import v10_3_demo_data_profiles


def main() -> int:
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("V10_3_DEMO_PROFILES.md")
    output.write_text(v10_3_demo_data_profiles()["content"], encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
