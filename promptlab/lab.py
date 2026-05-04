from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from promptlab.datasets import DatasetLoader
from promptlab.evaluator import Evaluator
from promptlab.metrics.llm_judge import HeuristicJudge
from promptlab.model import Model, default_model
from promptlab.prompt_versioner import PromptRepository
from promptlab.report_generator import ReportGenerator
from promptlab.types import EvaluationResult, PromptSpec


@dataclass
class PromptFaberLab:
    model: Model
    prompt_repo: PromptRepository
    dataset_loader: DatasetLoader
    evaluator: Evaluator
    report_generator: ReportGenerator

    @classmethod
    def create(
        cls,
        *,
        model: str | None = None,
        prompts_dir: str | Path = ".promptlab/prompts",
    ) -> "PromptFaberLab":
        model_obj = default_model(model)
        repo = PromptRepository(Path(prompts_dir))
        judge = HeuristicJudge()
        evaluator = Evaluator(model=model_obj, judge=judge)
        return cls(
            model=model_obj,
            prompt_repo=repo,
            dataset_loader=DatasetLoader(),
            evaluator=evaluator,
            report_generator=ReportGenerator(),
        )

    def evaluate(
        self,
        *,
        prompt_template: str | None = None,
        prompt_file: str | Path | None = None,
        test_cases: str | Path,
        criteria: list[str],
    ) -> EvaluationResult:
        prompt = self._resolve_prompt(prompt_template=prompt_template, prompt_file=prompt_file)
        dataset_name, cases = self.dataset_loader.load(Path(test_cases))
        return self.evaluator.evaluate(prompt=prompt, dataset_name=dataset_name, cases=cases, criteria=criteria)

    def compare(self, a: EvaluationResult, b: EvaluationResult) -> dict:
        return {
            "a": a.summary.model_dump(),
            "b": b.summary.model_dump(),
            "delta": {
                "avg_latency_ms": b.summary.avg_latency_ms - a.summary.avg_latency_ms,
                "avg_score": b.summary.avg_score - a.summary.avg_score,
                "accuracy": (b.summary.accuracy or 0.0) - (a.summary.accuracy or 0.0),
            },
        }

    def save_report(self, result: EvaluationResult, output_path: str | Path) -> Path:
        return self.report_generator.save(result, Path(output_path))

    def _resolve_prompt(
        self,
        *,
        prompt_template: str | None,
        prompt_file: str | Path | None,
    ) -> PromptSpec:
        if prompt_template and prompt_file:
            raise ValueError("Use apenas um: prompt_template OU prompt_file.")
        if prompt_file:
            return self.prompt_repo.load_from_file(Path(prompt_file))
        if prompt_template:
            return PromptSpec(name="inline", version="dev", template=prompt_template)
        raise ValueError("Informe prompt_template ou prompt_file.")
