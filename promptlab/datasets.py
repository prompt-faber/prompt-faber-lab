from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from promptlab.types import TestCase


class DatasetLoader:
    def load(self, dataset_path: Path) -> tuple[str, list[TestCase]]:
        if dataset_path.suffix.lower() == ".json":
            return self._load_json(dataset_path)
        if dataset_path.suffix.lower() == ".csv":
            return self._load_csv(dataset_path)
        raise ValueError("Dataset inválido: use .json ou .csv")

    def _load_json(self, dataset_path: Path) -> tuple[str, list[TestCase]]:
        raw = json.loads(dataset_path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            return dataset_path.name, [self._coerce_case(item) for item in raw]
        if isinstance(raw, dict) and "cases" in raw:
            name = str(raw.get("name") or dataset_path.name)
            cases_raw = raw["cases"]
            if not isinstance(cases_raw, list):
                raise ValueError("Dataset JSON inválido: 'cases' deve ser uma lista.")
            return name, [self._coerce_case(item) for item in cases_raw]
        raise ValueError("Dataset JSON inválido: esperado lista ou objeto com 'cases'.")

    def _load_csv(self, dataset_path: Path) -> tuple[str, list[TestCase]]:
        df = pd.read_csv(dataset_path)
        cases: list[TestCase] = []
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            case_id = _string_or_none(row_dict.pop("id", None))
            expected = _string_or_none(row_dict.pop("expected", None))
            cases.append(TestCase(id=case_id, input=_to_jsonable_dict(row_dict), expected=expected))
        return dataset_path.name, cases

    def _coerce_case(self, item: Any) -> TestCase:
        if not isinstance(item, dict):
            raise ValueError("Cada item do dataset deve ser um objeto.")
        input_obj = item.get("input") if "input" in item else item.get("inputs")
        if not isinstance(input_obj, dict):
            raise ValueError("Cada caso deve conter 'input' como objeto.")
        return TestCase(
            id=_string_or_none(item.get("id")),
            input=_to_jsonable_dict(input_obj),
            expected=_string_or_none(item.get("expected")),
        )


def _string_or_none(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _to_jsonable_dict(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("Esperado objeto (dict).")
    return {str(k): v for k, v in value.items()}
