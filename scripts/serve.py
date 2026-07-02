#!/usr/bin/env python
"""Run DevFlow Guard locally with one command.

Ensures the database schema and a default admin user exist, then starts the
API server. For personal/local use it disables the login screen by default so
you land straight in the app; pass ``--auth`` to keep authentication on.

    python scripts/serve.py            # no login, http://127.0.0.1:8000
    python scripts/serve.py --auth     # keep the login screen
    python scripts/serve.py --reload   # auto-reload while editing code
    python scripts/serve.py --port 9000
"""

import argparse
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

# Decide auth mode before importing the app, since settings read env at import.
# Default: no login for local convenience. `--auth` opts back in.
if "--auth" not in sys.argv:
    os.environ.setdefault("LOCAL_NO_AUTH", "true")

import uvicorn  # noqa: E402

from app import seed  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DevFlow Guard locally.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default 127.0.0.1).")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default 8000).")
    parser.add_argument("--reload", action="store_true", help="Auto-reload on code changes.")
    parser.add_argument("--auth", action="store_true", help="Keep the login screen enabled.")
    args = parser.parse_args()

    # Idempotent: creates tables and the admin@example.com account if missing.
    seed.main()

    no_auth = os.environ.get("LOCAL_NO_AUTH") == "true" and not args.auth
    print(f"\nDevFlow Guard is starting at http://{args.host}:{args.port}")
    if no_auth:
        print("Login is disabled for local use (run with --auth to enable it).\n")
    else:
        print("Sign in with admin@example.com / password123 (change it after first login).\n")
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
