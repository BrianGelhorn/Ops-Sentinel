# Ops-Sentinel

## Overview

Ops-Sentinel is a backend API project focused on service monitoring and incident management.

The system periodically checks configured services, detects failures, stores incident data and collects evidence related to each failure. The goal is to simulate a basic DevOps/SRE workflow involving monitoring, incident creation, evidence collection and resolution tracking.

## Features

- Service health monitoring
- Automatic incident creation with relevant information for troubleshooting when a monitored service fails
- Evidence collection for each incident
- Incident status tracking
- Resolution information storage
- PostgreSQL database integration
- Docker-based local environment

## Tech Stack
- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Docker / Docker Compose
- GitHub Actions

## Local Setup

```bash
git clone https://github.com/BrianGelhorn/Ops-Sentinel.git
cd Ops-Sentinel
cp .env.example .env
docker compose up --build
```

## Deployment integration check

Run the real Docker Compose deployment path before merging changes that affect startup, migrations, or database connectivity:

```bash
./scripts/integration_deploy_check.sh
```

The script loads `.env` when present, otherwise it falls back to `.env.example`. It starts an isolated Compose project with `docker compose up --build -d`, waits for the `db` service healthcheck to report `healthy`, verifies that `alembic upgrade head` succeeds inside the running `api` container, waits until `/ready` returns `{"status": "ready"}`, creates a monitor through `POST /monitor/`, and confirms that the monitor row exists in PostgreSQL.

Useful overrides:

```bash
ENV_FILE=.env.example COMPOSE_PROJECT_NAME=ops-sentinel-it APP_PORT=8000 ./scripts/integration_deploy_check.sh
KEEP_COMPOSE_STACK=1 ./scripts/integration_deploy_check.sh
```

By default the script tears the stack down with volumes after it finishes. Set `KEEP_COMPOSE_STACK=1` to keep the containers running for debugging.

## Documentation

- [Incident Lifecycle](docs/incident-lifecycle.md)
