from datetime import timedelta, datetime
import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise Exception("'JWT_SECRET' is not set in environment")


def decode_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, verify=False)
    except Exception:
        return None


def verify_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET)
    except Exception:
        return None


def generate_token(payload: dict[str, str], expires_in: timedelta = timedelta(days=7)):
    # add creation and expiration date to the payload
    payload["iat"] = datetime.now().isoformat()
    payload["ex"] = (datetime.now() + expires_in).isoformat()
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
