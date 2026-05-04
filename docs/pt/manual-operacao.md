# Prompt Faber Lab — Manual de Operação

## Pré-requisitos
- Docker e Docker Compose
- Acesso ao repositório e variáveis de ambiente (segredos)

## Ambientes
- Desenvolvimento: `docker-compose.yml` (serviços locais)
- Staging/Produção: infraestrutura via Terraform (AWS) em `infra/terraform/aws`

## Subir o ambiente (Desenvolvimento)

```bash
docker compose up --build
```

Serviços:
- Auth: http://localhost:8000/docs
- Core: http://localhost:8001/docs
- Report: http://localhost:8002/docs
- Dashboard: http://localhost:8501
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Kibana: http://localhost:5601

## Credenciais padrão (Desenvolvimento)
- Usuário: `admin@promptlab.local`
- Senha: `admin123`

Recomendação: trocar imediatamente em ambientes não-locais.

## Migrações
As migrações rodam automaticamente no container (`alembic upgrade head`).
Para rodar manualmente:

```bash
alembic upgrade head
```

## Backup e Restore (Postgres)

### Backup
```bash
pg_dump -h <host> -U <user> -F c -f backup.dump <db>
```

### Restore
```bash
pg_restore -h <host> -U <user> -d <db> --clean backup.dump
```

## Troubleshooting

### 1) Erros 401 (Não autenticado)
- Verificar JWT no header `Authorization: Bearer <token>`
- Verificar `PROMPTLAB_JWT_SECRET` consistente entre serviços

### 2) Erros 429 (Rate limit)
- Ajustar `PROMPTLAB_RATE_LIMIT` (ex.: `120/minute`)
- Validar IP/ingress em produção (proxy pode alterar origem)

### 3) Problemas de banco
- Checar URL `PROMPTLAB_DATABASE_URL`
- Checar status do Postgres e logs do container
- Verificar se migrações aplicaram (`alembic current`)

### 4) PDF não gera
- Instalar extra de relatórios: `promptlab[reports]`
- No Docker Compose o serviço `report` já compila com extra `reports`

### 5) Logs não aparecem no Kibana
- Verificar se Logstash está recebendo (porta UDP 12201)
- Verificar índice `promptlab-*` no Elasticsearch

## Alta disponibilidade e escala horizontal
- Em containers: escalar serviços stateless (`core`, `auth`, `report`) mantendo Postgres gerenciado.
- Em cloud (AWS/ECS): `desired_count >= 2` para múltiplas tasks por serviço.
- Ajustar autoscaling por CPU/RPS conforme carga (recomendado para ≥10.000 usuários simultâneos).
