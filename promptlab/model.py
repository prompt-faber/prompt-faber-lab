from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Protocol

import httpx


class Model(Protocol):
    name: str

    def generate(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class EchoModel:
    name: str = "echo"

    def generate(self, prompt: str) -> str:
        return prompt


@dataclass(frozen=True)
class OpenAICompatHttpModel:
    name: str
    base_url: str
    api_key: str
    model: str
    timeout_s: float = 30.0

    def generate(self, prompt: str) -> str:
        start = time.perf_counter()
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        with httpx.Client(base_url=self.base_url, timeout=self.timeout_s) as client:
            resp = client.post("/v1/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        _ = time.perf_counter() - start
        return data["choices"][0]["message"]["content"]


def default_model(model_name: str | None = None) -> Model:
    model_name = (model_name or os.getenv("PROMPTLAB_MODEL") or "echo").strip()
    if model_name == "echo":
        return EchoModel()

    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com")
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY não configurada para usar um modelo HTTP compatível com OpenAI.")
    return OpenAICompatHttpModel(
        name=f"openai-compat:{model_name}",
        base_url=base_url,
        api_key=api_key,
        model=model_name,
    )
