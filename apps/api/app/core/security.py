from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.settings import settings


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padded = value + "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(padded)


def sign_state(payload: dict, expires_in_sec: int = 600) -> str:
    now = datetime.now(timezone.utc)
    data = {
        **payload,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in_sec)).timestamp()),
    }
    encoded = _b64url_encode(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    sig = hmac.new(settings.app_secret.encode("utf-8"), encoded.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{encoded}.{sig}"


def verify_state(state: str) -> Optional[dict]:
    if "." not in state:
        return None

    encoded, sig = state.rsplit(".", 1)
    expected = hmac.new(settings.app_secret.encode("utf-8"), encoded.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        return None

    payload = json.loads(_b64url_decode(encoded).decode("utf-8"))
    now_ts = int(datetime.now(timezone.utc).timestamp())
    if now_ts > int(payload.get("exp", 0)):
        return None
    return payload
