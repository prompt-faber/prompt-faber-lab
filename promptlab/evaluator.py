from __future__ import annotations

import time
from dataclasses import dataclass

from promptlab.metrics.llm_judge import HeuristicJudge
from promptlab.model import Model
from promptlab.resilience import ResiliencePolicy, call_with_resilience
from promptlab.types import CaseResult, EvaluationResult, EvaluationSummary, PromptSpec, TestCase


@dataclass(frozen=True)
class Evaluator:
    model: Model
    judge: HeuristicJudge
    policy: ResiliencePolicy = ResiliencePolicy()

    def evaluate(
        self,
        *,
        prompt: PromptSpec,
        dataset_name: str,
        cases: list[TestCase],
        criteria: list[str],
    ) -> EvaluationResult:
        results: list[CaseResult] = []
        for case in cases:
            rendered = _render(prompt.template, case.input)
            start = time.perf_counter()

            def _do_generate() -> str:
                return self.model.generate(rendered)

            output = call_with_resilience(_do_generate, self.policy)
            latency_ms = (time.perf_counter() - start) * 1000.0
            scores = self.judge.score(rendered, output, criteria)
            passed = _passed(case.expected, output)
            results.append(
                CaseResult(
                    case_id=case.id,
                    rendered_prompt=rendered,
                    output=output,
                    latency_ms=latency_ms,
                    scores=scores,
                    passed=passed,
                )
            )

        summary = _summarize(
            prompt=prompt,
            dataset_name=dataset_name,
            model_name=self.model.name,
            criteria=criteria,
            results=results,
        )
        return EvaluationResult(summary=summary, cases=results)


def _render(template: str, values: dict) -> str:
    try:
        return template.format(**values)
    except KeyError as exc:
        raise ValueError(f"Dataset não contém chave necessária para o template: {exc}") from exc


def _passed(expected: str | None, output: str) -> bool | None:
    if expected is None:
        return None
    return expected.strip() == output.strip()


def _summarize(
    *,
    prompt: PromptSpec,
    dataset_name: str,
    model_name: str,
    criteria: list[str],
    results: list[CaseResult],
) -> EvaluationSummary:
    created_at = _now()
    avg_latency = sum(r.latency_ms for r in results) / max(1, len(results))
    avg_score = _avg_score(results)
    accuracy = _accuracy(results)
    return EvaluationSummary(
        prompt_name=prompt.name,
        prompt_version=prompt.version,
        dataset_name=dataset_name,
        model=model_name,
        created_at=created_at,
        criteria=criteria,
        avg_latency_ms=avg_latency,
        avg_score=avg_score,
        accuracy=accuracy,
    )


def _avg_score(results: list[CaseResult]) -> float:
    if not results:
        return 0.0
    totals: list[float] = []
    for r in results:
        if not r.scores:
            continue
        totals.append(sum(r.scores.values()) / len(r.scores))
    if not totals:
        return 0.0
    return sum(totals) / len(totals)


def _accuracy(results: list[CaseResult]) -> float | None:
    passed = [r for r in results if r.passed is not None]
    if not passed:
        return None
    ok = sum(1 for r in passed if r.passed)
    return (ok / len(passed)) * 100.0


def _now():
    from datetime import datetime, timezone

    return datetime.now(tz=timezone.utc)
