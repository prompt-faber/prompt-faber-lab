# Prompt Faber Lab — Documentação Técnica

## Visão Geral
O Prompt Faber Lab (pacote Python: `promptlab`) é um sistema modular para **testar, versionar e avaliar prompts** de forma reproduzível, oferecendo:

- CLI para execução rápida de avaliações e comparações A/B
- Microserviços HTTP com autenticação JWT e OpenAPI 3.0
- Geração de relatórios em JSON/HTML/Markdown (PDF opcional)
- Observabilidade com métricas Prometheus e dashboards Grafana
- Logs estruturados com pipeline ELK

## Arquitetura (Microserviços)

### Auth Service
- Responsabilidade: autenticação (login) e emissão de JWT.
- Endpoints principais:
  - `POST /auth/login`
- App: `promptlab.services.auth.app:app`

### Core Service
- Responsabilidade: CRUD de prompts e execução de avaliações.
- Endpoints principais:
  - `POST /prompts`
  - `GET /prompts`
  - `POST /evaluations`
- App: `promptlab.services.core.app:app`

### Report Service
- Responsabilidade: renderização de relatórios (HTML/JSON/MD/PDF).
- Endpoints principais:
  - `POST /reports/render`
- App: `promptlab.services.report.app:app`

### Dashboard
- Responsabilidade: interface web para criação de prompts e execução de avaliações.
- Script: `promptlab/dashboard.py`

## Módulos (Biblioteca Python)

### promptlab.lab
- Componente de alto nível para orquestrar avaliação, comparação e persistência de relatórios.

### promptlab.evaluator
- Executa o loop de avaliação: renderiza templates, chama modelo, mede latência e calcula métricas.
- Integra resiliência (retry + circuit breaker).

### promptlab.model
- Define adaptadores de modelo.
- Implementa `EchoModel` (offline) e `OpenAICompatHttpModel` (via HTTP compatível com OpenAI).

### promptlab.metrics.llm_judge
- Implementa um juiz heurístico determinístico para critérios como clareza e concisão.
- Pode ser substituído por um juiz real (LLM-as-Judge) mantendo a mesma interface.

### promptlab.report_generator
- Gera relatórios em `.json`, `.html`, `.md` e `.pdf` (quando instalado `promptlab[reports]`).

### promptlab.prompt_versioner
- Carrega prompts YAML e salva versões em diretório local, derivando `version` por hash quando necessário.

### promptlab.datasets
- Carrega datasets `.json` e `.csv` para casos de teste.

### promptlab.security
- JWT (criação/verificação) e hashing de senha (bcrypt via passlib).

### promptlab.resilience
- Políticas de resiliência: retry exponencial com jitter + circuit breaker.

### promptlab.services.base
- Base para apps FastAPI: CORS, rate limiting, `/metrics` e handlers padronizados.

## API (OpenAPI 3.0)
Cada microserviço expõe:

- Swagger UI: `GET /docs`
- OpenAPI JSON: `GET /openapi.json`

## Banco de Dados e Migrações
- ORM: SQLAlchemy
- Migrações: Alembic (`alembic/`, `alembic.ini`)
- Tabelas principais: `users`, `prompts`, `evaluations`

## Containerização
- `docker-compose.yml` sobe: Postgres, microserviços, dashboard, Prometheus/Grafana e ELK.

## Segurança
- Autenticação: JWT via header `Authorization: Bearer <token>`
- Rate limiting: SlowAPI (`PROMPTLAB_RATE_LIMIT`)
- CORS: `PROMPTLAB_CORS_ORIGINS`

## Observabilidade
- Métricas: `GET /metrics` (Prometheus)
- Dashboards: Grafana (porta 3000)
- Logs: ELK (Elasticsearch 9200, Kibana 5601)
