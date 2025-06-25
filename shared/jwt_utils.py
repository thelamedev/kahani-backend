from datetime import timedelta, datetime
from typing import Any
import jwt
import os

JWT_ALGORITHM = "HS256"
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
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except Exception as e:
        print(e)
        return None


def generate_token(payload: dict[str, Any], expires_in: timedelta = timedelta(days=7)):
    # add creation and expiration date to the payload
    payload["iat"] = int(datetime.now().timestamp())
    payload["ex"] = (datetime.now() + expires_in).timestamp()
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
