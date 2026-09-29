"""Short-lived, signed bearer tokens for authenticated API requests."""
import base64
import binascii
import hashlib
import hmac
import json
import logging
import os
import secrets
import time

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database.db_engine import get_db
from database.db_models import User


logger = logging.getLogger(__name__)
_configured_secret = os.getenv("SESSION_SECRET", "")
if _configured_secret:
    _secret = _configured_secret.encode("utf-8")
else:
    _secret = secrets.token_bytes(32)
    logger.warning("SESSION_SECRET belum diset; sesi login akan berakhir saat server dimulai ulang.")

_bearer = HTTPBearer(auto_error=False)
_token_lifetime = 12 * 60 * 60


def _encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _decode(data: str) -> bytes:
    padded = data + "=" * (-len(data) % 4)
    return base64.b64decode(padded, altchars=b"-_", validate=True)


def create_access_token(user: User) -> str:
    payload = _encode(json.dumps({"sub": user.id, "exp": int(time.time()) + _token_lifetime}, separators=(",", ":")).encode("utf-8"))
    signature = _encode(hmac.new(_secret, payload.encode("ascii"), hashlib.sha256).digest())
    return f"{payload}.{signature}"


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(status_code=401, detail="Sesi tidak valid atau sudah berakhir.", headers={"WWW-Authenticate": "Bearer"})
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized
    try:
        payload, signature = credentials.credentials.split(".", 1)
        expected = hmac.new(_secret, payload.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(_decode(signature), expected):
            raise unauthorized
        claims = json.loads(_decode(payload))
        if not isinstance(claims.get("sub"), int) or not isinstance(claims.get("exp"), int) or claims["exp"] <= time.time():
            raise unauthorized
    except (ValueError, UnicodeError, TypeError, binascii.Error):
        raise unauthorized from None
    user = db.get(User, claims["sub"])
    if user is None:
        raise unauthorized
    return user
