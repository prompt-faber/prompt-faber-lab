from __future__ import annotations

import math
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class HeuristicJudge:
    def score(self, rendered_prompt: str, output: str, criteria: list[str]) -> dict[str, float]:
        scores: dict[str, float] = {}
        for criterion in criteria:
            scores[criterion] = float(_score_one(criterion, rendered_prompt, output))
        return scores


def _score_one(criterion: str, rendered_prompt: str, output: str) -> float:
    criterion = criterion.strip().lower()
    if criterion in {"clarity", "clareza"}:
        return _clarity(output)
    if criterion in {"conciseness", "concisao", "concisão"}:
        return _conciseness(output)
    if criterion in {"factual_accuracy", "factualidade", "precisao_factual"}:
        return _factuality_proxy(output)
    if criterion in {"usefulness", "utilidade"}:
        return _usefulness_proxy(rendered_prompt, output)
    return _generic(output)


def _clarity(text: str) -> float:
    if not text.strip():
        return 0.0
    sentence_count = max(1, len(re.split(r"[.!?]+", text.strip())) - 1)
    avg_len = len(text) / sentence_count
    penalty = max(0.0, (avg_len - 180.0) / 60.0)
    return _clamp_0_10(9.0 - penalty)


def _conciseness(text: str) -> float:
    length = len(text.strip())
    if length == 0:
        return 0.0
    ideal = 500.0
    score = 10.0 - (abs(length - ideal) / ideal) * 6.0
    return _clamp_0_10(score)


def _factuality_proxy(text: str) -> float:
    if not text.strip():
        return 0.0
    hedges = len(re.findall(r"\b(maybe|perhaps|possibly|acho|talvez|pode ser)\b", text, flags=re.I))
    exclam = text.count("!")
    penalty = 0.6 * hedges + 0.3 * exclam
    return _clamp_0_10(8.5 - penalty)


def _usefulness_proxy(prompt: str, output: str) -> float:
    if not output.strip():
        return 0.0
    prompt_tokens = set(_tokens(prompt))
    out_tokens = set(_tokens(output))
    if not prompt_tokens or not out_tokens:
        return 6.0
    jacc = len(prompt_tokens & out_tokens) / max(1, len(prompt_tokens | out_tokens))
    return _clamp_0_10(6.0 + 4.0 * math.sqrt(jacc))


def _generic(text: str) -> float:
    if not text.strip():
        return 0.0
    return 7.0


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-zA-ZÀ-ÿ0-9_]+", text.lower()) if len(t) >= 3]


def _clamp_0_10(value: float) -> float:
    return max(0.0, min(10.0, value))
