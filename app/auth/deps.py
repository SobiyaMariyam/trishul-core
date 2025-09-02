from fastapi import Header, HTTPException
from typing import Optional
from app.auth.tokens import verify_token

def get_current_claims(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        claims = verify_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return claims
