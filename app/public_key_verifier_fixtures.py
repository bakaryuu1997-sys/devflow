from __future__ import annotations

import base64
from hashlib import sha256
from pathlib import Path
from typing import Any

FIXTURE_DIR = Path("fixtures/signature_adapters/ed25519_public_key_sample")
ADAPTER_ID = "ed25519-public-key"


def fixture_metadata() -> dict:
    files = {
        "payload": FIXTURE_DIR / "payload.txt",
        "public_key": FIXTURE_DIR / "public_key.pem",
        "signature": FIXTURE_DIR / "signature.b64",
    }
    rows = []
    combined = ""
    for name, path in files.items():
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        combined += text
        rows.append(_file_row(name, path, text))
    return {
        "adapter": ADAPTER_ID,
        "directory": str(FIXTURE_DIR),
        "all_files_present": all(row["exists"] for row in rows),
        "files": rows,
        "contains_private_key_marker": contains_private_key_marker(combined),
    }


def load_fixture_evidence() -> dict:
    payload = _read_bytes(FIXTURE_DIR / "payload.txt")
    public_key = _read_text(FIXTURE_DIR / "public_key.pem")
    signature_text = _read_text(FIXTURE_DIR / "signature.b64").strip()
    return build_evidence(payload, public_key, signature_text)


def request_evidence(request: dict[str, Any]) -> dict:
    payload_text = request.get("payload_text") or ""
    return build_evidence(
        payload_text.encode("utf-8"),
        request.get("public_key_pem") or "",
        request.get("signature_b64") or "",
    )


def build_evidence(payload_bytes: bytes, public_key_pem: str, signature_b64: str) -> dict:
    try:
        signature_bytes = base64.b64decode(signature_b64, validate=True) if signature_b64 else b""
    except Exception:
        signature_bytes = b""
    return {"payload_bytes": payload_bytes, "public_key_pem": public_key_pem, "signature_bytes": signature_bytes}


def contains_private_key_marker(text: str) -> bool:
    upper = text.upper()
    markers = ["BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "BEGIN EC PRIVATE KEY", "PRIVATE KEY-----"]
    return any(marker in upper for marker in markers)


def _file_row(name: str, path: Path, text: str) -> dict:
    return {
        "name": name,
        "path": str(path),
        "exists": path.exists(),
        "size_bytes": len(text.encode("utf-8")),
        "sha256": sha256(text.encode("utf-8")).hexdigest() if text else "",
    }


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes() if path.exists() else b""
