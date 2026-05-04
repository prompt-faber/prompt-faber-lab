# Prompt Faber Lab — Operations Manual

## Prerequisites
- Docker and Docker Compose
- Repository access and environment variables (secrets)

## Environments
- Development: `docker-compose.yml` (local services)
- Staging/Production: Terraform (AWS) under `infra/terraform/aws`

## Start (Development)

```bash
docker compose up --build
```

Services:
- Auth: http://localhost:8000/docs
- Core: http://localhost:8001/docs
- Report: http://localhost:8002/docs
- Dashboard: http://localhost:8501
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Kibana: http://localhost:5601

## Default Credentials (Development)
- User: `admin@promptlab.local`
- Password: `admin123`

Recommendation: change immediately in non-local environments.

## Migrations
Migrations run automatically in containers (`alembic upgrade head`).
To run manually:

```bash
alembic upgrade head
```

## Backup and Restore (Postgres)

### Backup
```bash
pg_dump -h <host> -U <user> -F c -f backup.dump <db>
```

### Restore
```bash
pg_restore -h <host> -U <user> -d <db> --clean backup.dump
```

## Troubleshooting

### 1) 401 errors (Unauthorized)
- Check JWT in `Authorization: Bearer <token>`
- Ensure `PROMPTLAB_JWT_SECRET` is consistent across services

### 2) 429 errors (Rate limit)
- Adjust `PROMPTLAB_RATE_LIMIT` (e.g., `120/minute`)
- Validate source IP behavior behind proxies in production

### 3) Database issues
- Check `PROMPTLAB_DATABASE_URL`
- Inspect Postgres/container health and logs
- Confirm migrations applied (`alembic current`)

### 4) PDF generation fails
- Install reports extra: `promptlab[reports]`
- In Docker Compose the `report` service is built with `reports` extra

### 5) Logs not visible in Kibana
- Ensure Logstash is receiving UDP (port 12201)
- Check `promptlab-*` index in Elasticsearch

## High availability and horizontal scaling
- In containers: scale stateless services (`core`, `auth`, `report`) with managed Postgres.
- In cloud (AWS/ECS): keep `desired_count >= 2` tasks per service.
- Add autoscaling rules (CPU/RPS) for sustained load (recommended for ≥10,000 concurrent users).
