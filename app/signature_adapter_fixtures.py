from __future__ import annotations

from hashlib import sha256
from pathlib import Path

FIXTURE_DIR = Path("fixtures/signature_adapters")
FIXTURE_TYPES = {
    "pgp-stub": "pgp_detached_signature_sample.asc",
    "x509-cms-stub": "x509_cms_signature_sample.pem",
    "rfc3161-tsa-stub": "rfc3161_timestamp_token_sample.tsr",
}


def load_fixture_rows() -> list[dict]:
    rows = []
    for adapter, filename in FIXTURE_TYPES.items():
        path = FIXTURE_DIR / filename
        content = path.read_text(encoding="utf-8") if path.exists() else ""
        rows.append(
            {
                "adapter": adapter,
                "filename": filename,
                "exists": path.exists(),
                "size_bytes": len(content.encode("utf-8")),
                "sha256": sha256(content.encode("utf-8")).hexdigest() if content else "",
                "contains_private_key": _contains_private_key(content),
                "purpose": "public contract-test fixture without private keys",
            }
        )
    return rows


def _contains_private_key(content: str) -> bool:
    markers = ["BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY", "BEGIN EC PRIVATE KEY", "PRIVATE KEY-----"]
    upper = content.upper()
    return any(marker in upper for marker in markers)
