from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from jose import jwt

from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# Minimal in-memory users for tests / local dev
_USERS = {
    # username: (password, role)
    "analyst": ("secret123", "analyst"),
    "owner": ("secret123", "owner"),
}

class LoginIn(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(body: LoginIn, request: Request):
    # Validate user
    rec = _USERS.get(body.username)
    if not rec or rec[0] != body.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    role = rec[1]
    tenant: Optional[str] = getattr(request.state, "tenant", None)
    if not tenant:
        # For safety, require tenant on login so we can bind tid into JWT
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing tenant")

    now = datetime.utcnow()
    exp = now + timedelta(hours=4)

    claims = {
        "sub": body.username,
        "role": role,
        "tid": tenant,                 # <<< bind JWT to tenant for middleware check
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    token = jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return JSONResponse({"access_token": token, "token_type": "bearer"})
