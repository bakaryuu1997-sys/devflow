#!/usr/bin/env bash
# One-command local launcher for DevFlow Guard (macOS/Linux).
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  echo "Installing dependencies..."
  python -m pip install --upgrade pip >/dev/null
  python -m pip install -r requirements.txt
else
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

python scripts/serve.py "$@"
