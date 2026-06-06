import hashlib
from time import time

_blacklisted_tokens: dict[str, float] = {}


def blacklist_token(token: str, expires_at: float | None = None) -> None:
    _blacklisted_tokens[_fingerprint(token)] = expires_at or (time() + 86400)


def is_token_blacklisted(token: str) -> bool:
    _cleanup()
    return _fingerprint(token) in _blacklisted_tokens


def reset_token_blacklist() -> None:
    _blacklisted_tokens.clear()


def _fingerprint(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _cleanup() -> None:
    now = time()
    expired = [key for key, expires_at in _blacklisted_tokens.items() if expires_at <= now]
    for key in expired:
        _blacklisted_tokens.pop(key, None)
