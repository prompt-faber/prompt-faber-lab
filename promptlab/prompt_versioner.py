from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

from promptlab.types import PromptSpec


class PromptRepository:
    def __init__(self, root_dir: Path) -> None:
        self._root_dir = root_dir
        self._root_dir.mkdir(parents=True, exist_ok=True)

    def load_from_file(self, prompt_path: Path) -> PromptSpec:
        data = yaml.safe_load(prompt_path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "template" in data:
            name = str(data.get("name") or prompt_path.stem)
            version = str(data.get("version") or self._derive_version(prompt_path))
            return PromptSpec(
                name=name,
                version=version,
                template=str(data["template"]),
                description_pt=data.get("description_pt"),
                description_en=data.get("description_en"),
            )
        if isinstance(data, str):
            return PromptSpec(
                name=prompt_path.stem,
                version=self._derive_version(prompt_path),
                template=data,
            )
        raise ValueError("Formato de prompt inválido: esperado YAML com campo 'template' ou string.")

    def save_version(self, spec: PromptSpec) -> Path:
        prompt_dir = self._root_dir / spec.name
        prompt_dir.mkdir(parents=True, exist_ok=True)
        out_path = prompt_dir / f"{spec.version}.yaml"
        out_path.write_text(
            yaml.safe_dump(_spec_to_yaml(spec), sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return out_path

    def _derive_version(self, prompt_path: Path) -> str:
        content = prompt_path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        return digest[:12]


def _spec_to_yaml(spec: PromptSpec) -> dict[str, Any]:
    data: dict[str, Any] = {
        "name": spec.name,
        "version": spec.version,
        "template": spec.template,
    }
    if spec.description_pt:
        data["description_pt"] = spec.description_pt
    if spec.description_en:
        data["description_en"] = spec.description_en
    return data
