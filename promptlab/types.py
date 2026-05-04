from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class PromptSpec(BaseModel):
    name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    template: str = Field(min_length=1)
    description_pt: str | None = None
    description_en: str | None = None


class TestCase(BaseModel):
    id: str | None = None
    input: dict[str, Any]
    expected: str | None = None


class CaseResult(BaseModel):
    case_id: str | None
    rendered_prompt: str
    output: str
    latency_ms: float
    scores: dict[str, float]
    passed: bool | None


class EvaluationSummary(BaseModel):
    prompt_name: str
    prompt_version: str
    dataset_name: str
    model: str
    created_at: datetime
    criteria: list[str]
    avg_latency_ms: float
    avg_score: float
    accuracy: float | None


class EvaluationResult(BaseModel):
    summary: EvaluationSummary
    cases: list[CaseResult]


class ReportFormat(BaseModel):
    format: Literal["json", "html", "md", "pdf"] = "json"
