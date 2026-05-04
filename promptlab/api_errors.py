from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from promptlab.logging_config import logger


class ErrorResponse(BaseModel):
    error: dict[str, Any]


def install_error_handlers(app: FastAPI) -> None:
    log = logger()

    @app.exception_handler(HTTPException)
    async def _http_exception_handler(request: Request, exc: HTTPException):  # noqa: ARG001
        trace_id = str(uuid.uuid4())
        log.info(
            "error.http_exception",
            trace_id=trace_id,
            status_code=exc.status_code,
            detail=str(exc.detail),
        )
        payload = {
            "error": {
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
                "status_code": exc.status_code,
                "trace_id": trace_id,
            }
        }
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(ValueError)
    async def _value_error_handler(request: Request, exc: ValueError):  # noqa: ARG001
        trace_id = str(uuid.uuid4())
        log.info("error.value_error", trace_id=trace_id, message=str(exc))
        payload = {"error": {"code": "VALIDATION_ERROR", "message": str(exc), "trace_id": trace_id}}
        return JSONResponse(status_code=422, content=payload)

    @app.exception_handler(Exception)
    async def _unhandled_handler(request: Request, exc: Exception):  # noqa: ARG001
        trace_id = str(uuid.uuid4())
        log.error("error.unhandled", trace_id=trace_id, exc_info=exc)
        payload = {"error": {"code": "INTERNAL_ERROR", "message": "Erro interno.", "trace_id": trace_id}}
        return JSONResponse(status_code=500, content=payload)
