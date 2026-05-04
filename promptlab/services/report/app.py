from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.responses import PlainTextResponse, Response
from pydantic import BaseModel

from promptlab.api_security import require_user
from promptlab.report_generator import ReportGenerator
from promptlab.types import EvaluationResult
from promptlab.services.base import create_base_app

app = create_base_app(title="Prompt Faber Lab — Report Service")


class RenderRequest(BaseModel):
    result: EvaluationResult
    format: str = "html"


@app.post("/reports/render", tags=["reports"])
def render(payload: RenderRequest, _claims: dict = Depends(require_user)):
    fmt = payload.format.lower().strip()
    generator = ReportGenerator()
    if fmt == "json":
        return Response(
            content=payload.result.model_dump_json(indent=2),
            media_type="application/json",
        )
    if fmt == "html":
        path = generator.save(payload.result, _tmp("report.html"))
        return Response(content=path.read_text(encoding="utf-8"), media_type="text/html; charset=utf-8")
    if fmt in {"md", "markdown"}:
        path = generator.save(payload.result, _tmp("report.md"))
        return PlainTextResponse(content=path.read_text(encoding="utf-8"))
    if fmt == "pdf":
        try:
            path = generator.save(payload.result, _tmp("report.pdf"))
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return Response(content=path.read_bytes(), media_type="application/pdf")
    raise HTTPException(status_code=400, detail="Formato inválido.")


def _tmp(name: str):
    from pathlib import Path
    import tempfile

    d = Path(tempfile.gettempdir()) / "promptlab"
    d.mkdir(parents=True, exist_ok=True)
    return d / name
