#!/usr/bin/env python
"""Run DevFlow Guard locally with one command.

Ensures the database schema and a default admin user exist, then starts the
API server. Intended for personal/local use::

    python scripts/serve.py            # http://127.0.0.1:8000
    python scripts/serve.py --reload   # auto-reload while editing code
    python scripts/serve.py --port 9000
"""

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import uvicorn  # noqa: E402

from app import seed  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DevFlow Guard locally.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1).")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default 8000).")
    parser.add_argument("--reload", action="store_true", help="Auto-reload on code changes.")
    args = parser.parse_args()

    # Idempotent: creates tables and the admin@example.com account if missing.
    seed.main()

    print(f"\nDevFlow Guard is starting at http://{args.host}:{args.port}")
    print("Sign in with admin@example.com / password123 (change it after first login).\n")
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
