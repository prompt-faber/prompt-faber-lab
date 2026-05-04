from __future__ import annotations

from pathlib import Path

from promptlab.report_generator import ReportGenerator
from promptlab.types import CaseResult, EvaluationResult, EvaluationSummary


def test_save_json_and_html(tmp_path: Path):
    result = EvaluationResult(
        summary=EvaluationSummary(
            prompt_name="p",
            prompt_version="v1",
            dataset_name="d",
            model="echo",
            created_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            criteria=["clarity"],
            avg_latency_ms=1.0,
            avg_score=8.0,
            accuracy=None,
        ),
        cases=[
            CaseResult(
                case_id="1",
                rendered_prompt="x",
                output="y",
                latency_ms=1.0,
                scores={"clarity": 8.0},
                passed=None,
            )
        ],
    )
    g = ReportGenerator()
    out_json = g.save(result, tmp_path / "r.json")
    assert out_json.exists()
    out_html = g.save(result, tmp_path / "r.html")
    assert "<html" in out_html.read_text(encoding="utf-8").lower()
