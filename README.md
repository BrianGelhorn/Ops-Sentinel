# Ops-Sentinel

Ops-Sentinel is a FastAPI backend for basic service monitoring and incident management. It lets users register HTTP monitors, runs scheduled checks against those services, creates incidents when checks fail, and stores the evidence needed to review each failure.

The project is intentionally small, but it follows a real DevOps/SRE-style workflow: detect a failure, create an incident, collect trigger/evidence data, and let an operator update the incident when the issue is understood or resolved.

## Features

- HTTP service monitoring with configurable expected status codes.
- Background scheduler that periodically runs monitor checks.
- Automatic incident creation when a monitor fails.
- Incident filtering by id, title, service, type, severity and source.
- Manual incident updates for status, summary, severity and resolution details.
- Evidence collection with response time, CPU usage, memory usage and error message.
- PostgreSQL persistence through SQLAlchemy.
- Alembic migrations for database schema changes.
- Docker Compose environment for local execution.
- GitHub Actions workflows for tests, image build and deployment checks.

## Tech Stack

- Python 3.13
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- HTTPX
- Pytest
- Docker / Docker Compose
- GitHub Actions

## Project Structure

```text
.
├── database/      # SQLAlchemy engine/session setup, models and CRUD helpers
├── docs/          # Project documentation
├── migrations/    # Alembic migration files
├── routers/       # FastAPI route modules
├── schemas/       # Pydantic request/response models
├── services/      # Monitor creation and check execution logic
├── tests/         # Automated tests
├── workers/       # Background scheduler
├── Dockerfile
├── docker-compose.yml
├── main.py
└── requirements.txt
```

## Local Setup

1. Clone the repository:

```bash
git clone https://github.com/BrianGelhorn/Ops-Sentinel.git
cd Ops-Sentinel
```

2. Create the environment file:

```bash
cp .env.example .env
```

3. Start the application and database:

```bash
docker compose up --build
```

4. Check that the API is running:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Expected responses:

```json
{"status":"alive"}
```

```json
{"status":"ready"}
```

The API is available at `http://localhost:8000` by default.

## Environment Variables

The default values for local development are documented in `.env.example`.

| Variable | Description |
| --- | --- |
| `APP_PORT` | Host port used to expose the FastAPI application. |
| `POSTGRES_DB` | PostgreSQL database name. |
| `POSTGRES_USER` | PostgreSQL username. |
| `POSTGRES_PASSWORD` | PostgreSQL password. |
| `DB_PORT` | Host port used to expose PostgreSQL. |
| `POSTGRES_DB_TEST` | Database name used by the test database container. |
| `DB_PORT_TEST` | Host port used to expose the test PostgreSQL container. |

## Database Migrations

The application uses Alembic to manage database schema changes. The Docker container runs migrations before starting the API:

```bash
alembic upgrade head
```

To run migrations manually inside the API container:

```bash
docker compose exec api alembic upgrade head
```

## API Endpoints

### Health and readiness

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Confirms the API process is alive. |
| `GET` | `/ready` | Confirms the API can connect to the database. |

### Monitors

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/monitor/` | Creates a new HTTP monitor. |
| `GET` | `/monitor/` | Lists all configured monitors. |
| `GET` | `/monitor/get_active_incidents?monitorid={id}` | Lists unresolved incidents for a monitor. |

Example monitor payload:

```json
{
  "title": "Example service",
  "type": "http",
  "interval_seconds": 60,
  "config": {
    "url": "https://example.com",
    "expected_status": 200
  }
}
```

### Incidents

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/incidents` | Lists incidents, with optional filters. |
| `GET` | `/incidents/{id}` | Gets one incident by id. |
| `POST` | `/incidents/` | Creates an incident manually. |
| `PATCH` | `/incidents/{id}` | Updates incident status, summary, severity or resolution details. |

Supported incident statuses:

- `open`
- `acknowledged`
- `resolved`

Example incident update:

```json
{
  "status": "resolved",
  "resolution": {
    "action_taken": "Restarted the affected service and reviewed logs",
    "action_result": "Service recovered",
    "date": "2026-05-11T12:00:00Z"
  }
}
```

## Incident Resolution Policy

Incidents are not automatically marked as resolved when a monitor starts passing again.

That is intentional: a successful check only proves that the service responded correctly at that moment. For intermittent failures, automatically closing the incident could hide an issue before the cause is understood. Resolution is a manual action so the operator can record what happened, what action was taken and why the incident can be closed.

For more detail, see [Incident Lifecycle](docs/incident-lifecycle.md).

## Running Tests

Install dependencies and run the test suite:

```bash
pip install -r requirements.txt pytest pytest-asyncio flake8
python -m pytest
```

Run the same lint check used by CI:

```bash
flake8 . --count --select=E,F63,F7,F82 --max-line-length=100
```

## Deployment Notes

The production workflow builds and publishes a Docker image, deploys it to the configured server, starts the Compose stack, and then verifies readiness through `/ready`.

The test workflow follows the same idea for the test environment. Both workflows keep `/health` as a basic liveness check and use `/ready` as the stronger deployment check because it validates database connectivity.

## Documentation

- [Incident Lifecycle](docs/incident-lifecycle.md)
