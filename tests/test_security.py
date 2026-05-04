from __future__ import annotations

import pytest

from promptlab.security import AuthError, create_access_token, hash_password, verify_password, verify_token


def test_password_hashing():
    h = hash_password("secret")
    assert verify_password("secret", h)
    assert not verify_password("wrong", h)


def test_jwt_roundtrip():
    token = create_access_token(subject="user-1", scopes=["a"])
    claims = verify_token(token)
    assert claims["sub"] == "user-1"
    assert claims["scopes"] == ["a"]


def test_jwt_invalid():
    with pytest.raises(AuthError):
        verify_token("not-a-token")
