"""Vercel serverless entrypoint.

Vercel's Python runtime detects the ASGI ``app`` exported here and routes all
requests to it (see ../vercel.json). We add the repository root to ``sys.path``
so the ``app`` package imports cleanly regardless of the function's CWD.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402  (import must follow the sys.path tweak)

__all__ = ["app"]
