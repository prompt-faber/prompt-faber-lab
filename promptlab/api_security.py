from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from promptlab.security import AuthError, verify_token

bearer = HTTPBearer(auto_error=False)


def require_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if not creds:
        raise HTTPException(status_code=401, detail="Não autenticado.")
    try:
        return verify_token(creds.credentials)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
