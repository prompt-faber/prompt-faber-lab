# Prompt Faber Lab — Technical Documentation

## Overview
Prompt Faber Lab (Python package: `promptlab`) is a modular system to **test, version, and evaluate prompts** reproducibly, providing:

- CLI for quick evaluations and A/B comparisons
- HTTP microservices with JWT authentication and OpenAPI 3.0
- Report generation in JSON/HTML/Markdown (PDF optional)
- Observability via Prometheus metrics and Grafana dashboards
- Structured logging with an ELK pipeline

## Architecture (Microservices)

### Auth Service
- Responsibility: authentication (login) and JWT issuance.
- Key endpoints:
  - `POST /auth/login`
- App: `promptlab.services.auth.app:app`

### Core Service
- Responsibility: prompt CRUD and evaluation execution.
- Key endpoints:
  - `POST /prompts`
  - `GET /prompts`
  - `POST /evaluations`
- App: `promptlab.services.core.app:app`

### Report Service
- Responsibility: report rendering (HTML/JSON/MD/PDF).
- Key endpoints:
  - `POST /reports/render`
- App: `promptlab.services.report.app:app`

### Dashboard
- Responsibility: web UI for prompt creation and running evaluations.
- Script: `promptlab/dashboard.py`

## Modules (Python Library)

### promptlab.lab
- High-level façade for evaluation, comparison, and report persistence.

### promptlab.evaluator
- Evaluation loop: renders templates, calls the model, measures latency, computes metrics.
- Includes resilience (retry + circuit breaker).

### promptlab.model
- Model adapters.
- Implements `EchoModel` (offline) and `OpenAICompatHttpModel` (OpenAI-compatible HTTP).

### promptlab.metrics.llm_judge
- Deterministic heuristic judge for criteria such as clarity and conciseness.
- Can be replaced by a real LLM-as-Judge using the same interface.

### promptlab.report_generator
- Generates `.json`, `.html`, `.md`, and `.pdf` (when `promptlab[reports]` is installed).

### promptlab.prompt_versioner
- Loads YAML prompts and stores versions locally; derives `version` from a hash when needed.

### promptlab.datasets
- Loads `.json` and `.csv` datasets into test cases.

### promptlab.security
- JWT utilities and password hashing (bcrypt via passlib).

### promptlab.resilience
- Resilience policies: exponential jitter retries + circuit breaker.

### promptlab.services.base
- FastAPI base setup: CORS, rate limiting, `/metrics`, standardized error handling.

## API (OpenAPI 3.0)
Each microservice exposes:

- Swagger UI: `GET /docs`
- OpenAPI JSON: `GET /openapi.json`

## Database and Migrations
- ORM: SQLAlchemy
- Migrations: Alembic (`alembic/`, `alembic.ini`)
- Core tables: `users`, `prompts`, `evaluations`

## Containerization
- `docker-compose.yml` brings up: Postgres, microservices, dashboard, Prometheus/Grafana, and ELK.

## Security
- Auth: JWT via `Authorization: Bearer <token>`
- Rate limiting: SlowAPI (`PROMPTLAB_RATE_LIMIT`)
- CORS: `PROMPTLAB_CORS_ORIGINS`

## Observability
- Metrics: `GET /metrics` (Prometheus)
- Dashboards: Grafana (port 3000)
- Logs: ELK (Elasticsearch 9200, Kibana 5601)
