#!/usr/bin/env python
"""Regenerate ``static/governance_bundle.js`` from the per-version modules.

The governance UI is authored as small ``governance_v*_ui.js`` source files.
They are concatenated (in dependency/load order) into a single bundle so the
page ships one ``<script>`` tag instead of ~20. Run this after editing any
source module::

    python scripts/build_governance_bundle.py
"""

from __future__ import annotations

import pathlib
import sys

STATIC = pathlib.Path(__file__).resolve().parents[1] / "static"
BUNDLE = STATIC / "governance_bundle.js"

# Load order matters: governance_v10_ui.js defines renderGenericGovernanceCard,
# which every later module relies on.
ORDER = [
    "governance_v10_ui.js",
    *[f"governance_v{n}_ui.js" for n in range(101, 121)],
]

HEADER = (
    "/* AUTO-GENERATED BUNDLE — do not edit directly.\n"
    " * Concatenation of the per-version governance UI modules, in load order.\n"
    " * Regenerate with scripts/build_governance_bundle.py after editing sources.\n"
    " */\n"
)


def build() -> str:
    parts = [HEADER, ""]
    for name in ORDER:
        src = STATIC / name
        if not src.exists():
            raise SystemExit(f"missing source module: {src}")
        parts.append(f"// ==== {name} ====")
        parts.append(src.read_text(encoding="utf-8").rstrip("\n"))
        parts.append("")
    return "\n".join(parts) + "\n"


def main() -> int:
    content = build()
    BUNDLE.write_text(content, encoding="utf-8")
    # Report via a relative path so output stays ASCII-safe on legacy consoles.
    rel = BUNDLE.relative_to(pathlib.Path.cwd()) if BUNDLE.is_relative_to(pathlib.Path.cwd()) else BUNDLE.name
    print(f"Wrote {rel} ({len(ORDER)} modules, {BUNDLE.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
