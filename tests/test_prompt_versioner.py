from __future__ import annotations

from pathlib import Path

import yaml

from promptlab.prompt_versioner import PromptRepository


def test_load_and_save_prompt(tmp_path: Path):
    repo = PromptRepository(tmp_path / "prompts")
    prompt_file = tmp_path / "p.yaml"
    prompt_file.write_text(
        yaml.safe_dump({"name": "resumo", "version": "v1", "template": "Oi {x}"}),
        encoding="utf-8",
    )

    spec = repo.load_from_file(prompt_file)
    assert spec.name == "resumo"
    assert spec.version == "v1"
    assert spec.template == "Oi {x}"

    saved = repo.save_version(spec)
    assert saved.exists()
    saved_spec = repo.load_from_file(saved)
    assert saved_spec == spec
