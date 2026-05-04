from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from promptlab.api_security import require_user
from promptlab.db import get_db
from promptlab.db_models import Evaluation, Prompt
from promptlab.evaluator import Evaluator
from promptlab.metrics.llm_judge import HeuristicJudge
from promptlab.model import default_model
from promptlab.types import EvaluationResult, PromptSpec, TestCase
from promptlab.services.base import create_base_app

app = create_base_app(title="Prompt Faber Lab — Core Service")


class CreatePromptRequest(BaseModel):
    name: str
    version: str
    template: str
    description_pt: str | None = None
    description_en: str | None = None


class PromptResponse(BaseModel):
    id: str
    name: str
    version: str
    template: str


class DatasetPayload(BaseModel):
    name: str
    cases: list[TestCase]


class EvaluateRequest(BaseModel):
    prompt_id: str
    dataset: DatasetPayload
    criteria: list[str] = ["clarity", "conciseness", "factual_accuracy"]
    model: str = "echo"


class EvaluateResponse(BaseModel):
    evaluation_id: str
    result: EvaluationResult


@app.post("/prompts", response_model=PromptResponse, tags=["prompts"])
def create_prompt(
    payload: CreatePromptRequest,
    db: Session = Depends(get_db),
    _claims: dict = Depends(require_user),
) -> PromptResponse:
    prompt = Prompt(
        id=str(uuid.uuid4()),
        name=payload.name,
        version=payload.version,
        template=payload.template,
    )
    db.add(prompt)
    db.commit()
    return PromptResponse(id=prompt.id, name=prompt.name, version=prompt.version, template=prompt.template)


@app.get("/prompts", response_model=list[PromptResponse], tags=["prompts"])
def list_prompts(
    db: Session = Depends(get_db),
    _claims: dict = Depends(require_user),
) -> list[PromptResponse]:
    prompts = db.query(Prompt).order_by(Prompt.created_at.desc()).limit(100).all()
    return [PromptResponse(id=p.id, name=p.name, version=p.version, template=p.template) for p in prompts]


@app.post("/evaluations", response_model=EvaluateResponse, tags=["evaluations"])
def evaluate(
    payload: EvaluateRequest,
    db: Session = Depends(get_db),
    _claims: dict = Depends(require_user),
) -> EvaluateResponse:
    prompt_row = db.query(Prompt).filter(Prompt.id == payload.prompt_id).first()
    if not prompt_row:
        raise HTTPException(status_code=404, detail="Prompt não encontrado.")

    prompt = PromptSpec(name=prompt_row.name, version=prompt_row.version, template=prompt_row.template)
    evaluator = Evaluator(model=default_model(payload.model), judge=HeuristicJudge())
    result = evaluator.evaluate(
        prompt=prompt,
        dataset_name=payload.dataset.name,
        cases=payload.dataset.cases,
        criteria=payload.criteria,
    )

    ev_id = str(uuid.uuid4())
    db.add(
        Evaluation(
            id=ev_id,
            prompt_id=prompt_row.id,
            dataset_name=payload.dataset.name,
            model=evaluator.model.name,
            criteria=payload.criteria,
            summary=result.summary.model_dump(),
        )
    )
    db.commit()
    return EvaluateResponse(evaluation_id=ev_id, result=result)
