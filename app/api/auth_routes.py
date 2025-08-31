from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from typing import Dict

from app.auth.jwt import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

# In-memory users for 2.1 acceptance tests ONLY.
# Keys = (tenant, username)
USERS: Dict[tuple, Dict[str, str]] = {
    ("tenant1", "analyst"): {"password": "secret123", "role": "analyst"},
    ("tenant1", "owner"): {"password": "secret123", "role": "owner"},
    ("tenant1", "admin"): {"password": "secret123", "role": "admin"},
}

class LoginIn(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(payload: LoginIn, request: Request):
    tenant = request.state.tenant
    if not tenant:
        # Must come via subdomain like tenant1.lvh.me
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="tenant not resolved from Host header",
        )

    key = (tenant, payload.username)
    rec = USERS.get(key)
    if not rec or rec["password"] != payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid credentials",
        )

    token = create_access_token(
        subject=payload.username,
        tenant=tenant,
        role=rec["role"],
        expires_minutes=60,
    )
    return {"access_token": token, "token_type": "bearer"}
