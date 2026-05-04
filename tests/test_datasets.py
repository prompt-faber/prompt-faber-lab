from __future__ import annotations

import json
from pathlib import Path

from promptlab.datasets import DatasetLoader


def test_load_json_list(tmp_path: Path):
    p = tmp_path / "d.json"
    p.write_text(
        json.dumps([{"id": "1", "input": {"text": "a"}, "expected": "b"}], ensure_ascii=False),
        encoding="utf-8",
    )
    name, cases = DatasetLoader().load(p)
    assert name == "d.json"
    assert len(cases) == 1
    assert cases[0].input["text"] == "a"


def test_load_json_object(tmp_path: Path):
    p = tmp_path / "d.json"
    p.write_text(
        json.dumps({"name": "bench", "cases": [{"input": {"x": 1}}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    name, cases = DatasetLoader().load(p)
    assert name == "bench"
    assert cases[0].input["x"] == 1


def test_load_csv(tmp_path: Path):
    p = tmp_path / "d.csv"
    p.write_text("id,expected,text\n1,ok,hello\n", encoding="utf-8")
    name, cases = DatasetLoader().load(p)
    assert name == "d.csv"
    assert cases[0].id == "1"
    assert cases[0].expected == "ok"
    assert cases[0].input["text"] == "hello"
