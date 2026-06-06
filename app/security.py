import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(subject: str) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=settings.access_token_minutes)
    payload = {"sub": subject, "exp": int(expires.timestamp()), "jti": uuid4().hex}
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = f"{_b64(header)}.{_b64(payload)}"
    signature = _sign(signing_input)
    return f"{signing_input}.{signature}"


def decode_access_token(token: str) -> str | None:
    try:
        header_raw, payload_raw, signature = token.split(".", 2)
        signing_input = f"{header_raw}.{payload_raw}"
        if not hmac.compare_digest(_sign(signing_input), signature):
            return None
        payload = json.loads(_b64decode(payload_raw))
        if int(payload.get("exp", 0)) < int(datetime.now(UTC).timestamp()):
            return None
        return str(payload.get("sub"))
    except Exception:
        return None


def _sign(value: str) -> str:
    digest = hmac.new(settings.jwt_secret_key.encode(), value.encode(), hashlib.sha256).digest()
    return _b64bytes(digest)


def _b64(data: dict) -> str:
    return _b64bytes(json.dumps(data, separators=(",", ":")).encode())


def _b64bytes(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64decode(value: str) -> str:
    padded = value + "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(padded.encode()).decode()
