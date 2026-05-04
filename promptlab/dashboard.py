from __future__ import annotations

import json
from dataclasses import dataclass

import httpx
import streamlit as st


@dataclass(frozen=True)
class ApiClient:
    base_url: str
    token: str

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    def list_prompts(self) -> list[dict]:
        with httpx.Client(base_url=self.base_url, timeout=15) as client:
            r = client.get("/prompts", headers=self._headers())
            r.raise_for_status()
            return r.json()

    def create_prompt(self, payload: dict) -> dict:
        with httpx.Client(base_url=self.base_url, timeout=15) as client:
            r = client.post("/prompts", json=payload, headers=self._headers())
            r.raise_for_status()
            return r.json()

    def evaluate(self, payload: dict) -> dict:
        with httpx.Client(base_url=self.base_url, timeout=60) as client:
            r = client.post("/evaluations", json=payload, headers=self._headers())
            r.raise_for_status()
            return r.json()


def main() -> None:
    st.set_page_config(page_title="Prompt Faber Lab", layout="wide")
    st.title("Prompt Faber Lab — Dashboard")

    st.sidebar.header("Configuração")
    base_url = st.sidebar.text_input("Core API URL", value="http://localhost:8001")
    token = st.sidebar.text_input("JWT", type="password", value="")

    if not token.strip():
        st.info("Informe um JWT para carregar dados.")
        return

    api = ApiClient(base_url=base_url.rstrip("/"), token=token.strip())

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Prompts")
        if st.button("Atualizar lista"):
            st.session_state["prompts"] = api.list_prompts()
        prompts = st.session_state.get("prompts") or []
        st.dataframe(prompts, use_container_width=True)

    with col_b:
        st.subheader("Criar prompt")
        name = st.text_input("Nome", value="resumo_v1")
        version = st.text_input("Versão", value="v1")
        template = st.text_area("Template", value="Resuma o texto a seguir em 3 frases: {text}", height=120)
        if st.button("Salvar"):
            created = api.create_prompt({"name": name, "version": version, "template": template})
            st.success("Prompt criado.")
            st.json(created)

    st.divider()
    st.subheader("Avaliar")
    prompt_id = st.text_input("Prompt ID")
    dataset_name = st.text_input("Dataset name", value="inline")
    cases_raw = st.text_area(
        "Cases (JSON)",
        value=json.dumps(
            [{"id": "1", "input": {"text": "Texto exemplo"}, "expected": None}],
            ensure_ascii=False,
            indent=2,
        ),
        height=180,
    )
    criteria = st.multiselect(
        "Critérios",
        options=["clarity", "conciseness", "factual_accuracy", "usefulness"],
        default=["clarity", "conciseness", "factual_accuracy"],
    )
    if st.button("Executar avaliação"):
        cases = json.loads(cases_raw)
        payload = {
            "prompt_id": prompt_id,
            "dataset": {"name": dataset_name, "cases": cases},
            "criteria": criteria,
            "model": "echo",
        }
        res = api.evaluate(payload)
        st.success("Avaliação concluída.")
        st.json(res)


if __name__ == "__main__":
    main()
