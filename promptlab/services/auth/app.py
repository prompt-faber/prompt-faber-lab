from __future__ import annotations

from fastapi import Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from promptlab.db import get_db
from promptlab.db_models import User
from promptlab.security import create_access_token, verify_password
from promptlab.seeders import seed_admin
from promptlab.services.base import create_base_app

app = create_base_app(title="Prompt Faber Lab — Auth Service")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@app.on_event("startup")
def _seed_admin() -> None:
    from promptlab.db import get_sessionmaker

    db = get_sessionmaker()()
    try:
        seed_admin(db)
    finally:
        db.close()


@app.post("/auth/login", response_model=LoginResponse, tags=["auth"])
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuário inativo.")
    token = create_access_token(subject=user.id, scopes=["promptlab:write", "promptlab:read"])
    return LoginResponse(access_token=token)
