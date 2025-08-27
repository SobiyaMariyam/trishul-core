from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from passlib.hash import bcrypt
from app.db.manager import get_core_db
from app.auth.tokens import create_token

router = APIRouter(prefix="/auth", tags=["auth"])

class SignupIn(BaseModel):
    username: str = Field(min_length=3)
    password: str = Field(min_length=6)
    tenant: str   = Field(min_length=2)

class LoginIn(BaseModel):
    username: str
    password: str
    tenant: str

@router.post("/signup")
def signup(body: SignupIn):
    core = get_core_db()
    if core.users.find_one({"username": body.username, "tenant": body.tenant}):
        raise HTTPException(status_code=400, detail="User already exists")
    core.users.insert_one({
        "username": body.username,
        "tenant": body.tenant,
        "password_hash": bcrypt.hash(body.password),
        "roles": ["owner"],
    })
    return {"ok": True}

@router.post("/login")
def login(body: LoginIn):
    core = get_core_db()
    doc = core.users.find_one({"username": body.username, "tenant": body.tenant})
    if not doc or not bcrypt.verify(body.password, doc.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": body.username, "tenant": body.tenant})
    return {"access_token": token, "token_type": "bearer"}
