"""Smoke tests for the local launcher (scripts/serve.py) and run wrappers."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_serve():
    spec = importlib.util.spec_from_file_location("serve", ROOT / "scripts" / "serve.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # top-level does not start the server
    return module


def test_serve_module_exposes_main():
    serve = _load_serve()
    assert callable(serve.main)


def test_run_wrappers_exist():
    assert (ROOT / "run.bat").exists()
    assert (ROOT / "run.sh").exists()
    # The launcher seeds via the shared seed module so login works out of the box.
    assert "seed.main()" in (ROOT / "scripts" / "serve.py").read_text(encoding="utf-8")
