import time
import jwt
from app.auth.config import JWT_SECRET, JWT_ALG


def create_token(data: dict, expires_in: int = 3600) -> str:
    payload = data.copy()
    payload["exp"] = int(time.time()) + expires_in
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
