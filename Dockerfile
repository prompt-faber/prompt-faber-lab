FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG PIP_EXTRAS=""

COPY pyproject.toml /app/pyproject.toml
COPY promptlab /app/promptlab
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic

RUN pip install --no-cache-dir -U pip && \
    if [ -n "$PIP_EXTRAS" ]; then pip install --no-cache-dir ".[${PIP_EXTRAS}]"; else pip install --no-cache-dir .; fi

EXPOSE 8000

CMD ["uvicorn", "promptlab.services.core.app:app", "--host", "0.0.0.0", "--port", "8000"]
