from __future__ import annotations

from fastapi.testclient import TestClient

from promptlab.services.auth.app import app as auth_app
from promptlab.services.core.app import app as core_app


def test_auth_and_core_flow():
    with TestClient(auth_app) as auth_client:
        r = auth_client.post(
            "/auth/login",
            json={"email": "admin@promptlab.local", "password": "admin123"},
        )
        assert r.status_code == 200
        token = r.json()["access_token"]

    with TestClient(core_app) as core_client:
        headers = {"Authorization": f"Bearer {token}"}
        r = core_client.post(
            "/prompts",
            json={"name": "resumo", "version": "v1", "template": "Resuma: {text}"},
            headers=headers,
        )
        assert r.status_code == 200
        prompt_id = r.json()["id"]

        r = core_client.post(
            "/evaluations",
            json={
                "prompt_id": prompt_id,
                "dataset": {
                    "name": "inline",
                    "cases": [{"id": "1", "input": {"text": "abc"}, "expected": "Resuma: abc"}],
                },
                "criteria": ["clarity"],
                "model": "echo",
            },
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["result"]["summary"]["accuracy"] == 100.0
