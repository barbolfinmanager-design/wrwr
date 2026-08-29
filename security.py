import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl
from config import config

class AuthError(Exception):
    pass

def validate_init_data(init_data: str, max_age_seconds: int = 86400) -> dict:
    """
    Telegram Mini App validation:
    secret_key = HMAC_SHA256(key="WebAppData", msg=BOT_TOKEN)
    received hash == HMAC_SHA256(key=secret_key, msg=data_check_string)
    """
    if config.dev_mode and not init_data:
        return {
            "id": config.dev_user_id,
            "first_name": "Dev",
            "username": "dev_user"
        }

    if not init_data or not config.bot_token:
        raise AuthError("Missing Telegram initData")

    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = pairs.pop("hash", None)
    pairs.pop("signature", None)
    if not received_hash:
        raise AuthError("Missing hash")

    auth_date = int(pairs.get("auth_date", "0") or "0")
    now = int(time.time())
    if auth_date <= 0 or now - auth_date > max_age_seconds or auth_date > now + 60:
        raise AuthError("Expired initData")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    secret_key = hmac.new(
        b"WebAppData",
        config.bot_token.encode("utf-8"),
        hashlib.sha256
    ).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise AuthError("Invalid initData")

    try:
        user = json.loads(pairs["user"])
    except Exception as e:
        raise AuthError("Missing user") from e

    if not isinstance(user.get("id"), int):
        raise AuthError("Invalid user")
    return user
