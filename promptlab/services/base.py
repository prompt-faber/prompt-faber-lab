from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from promptlab.api_errors import install_error_handlers
from promptlab.logging_config import configure_logging
from promptlab.settings import settings


def create_base_app(*, title: str, version: str = "0.1.0") -> FastAPI:
    configure_logging()
    app = FastAPI(title=title, version=version)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(SecurityHeadersMiddleware)

    limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)
    app.add_middleware(SlowAPIMiddleware)

    install_error_handlers(app)

    @app.get("/metrics", include_in_schema=False)
    def metrics():
        data = generate_latest(REGISTRY)
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    return app


def _rate_limit_handler(request, exc):  # noqa: ANN001,ARG001
    return Response(
        status_code=429,
        media_type="application/json",
        content='{"error":{"code":"RATE_LIMIT","message":"Muitas requisições."}}',
    )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):  # noqa: ANN001
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "geolocation=()")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
        )
        return response
