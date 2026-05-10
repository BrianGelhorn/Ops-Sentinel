#!/usr/bin/env bash
set -Eeuo pipefail

COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-ops-sentinel-it}"
ENV_FILE="${ENV_FILE:-.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  if [[ -f ".env.example" ]]; then
    ENV_FILE=".env.example"
  else
    echo "Neither .env nor .env.example exists; cannot provide compose variables." >&2
    exit 1
  fi
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

APP_PORT="${APP_PORT:-8000}"
POSTGRES_DB="${POSTGRES_DB:-ops_sentinel}"
POSTGRES_USER="${POSTGRES_USER:-ops_user}"
READY_TIMEOUT_SECONDS="${READY_TIMEOUT_SECONDS:-90}"
DB_HEALTH_TIMEOUT_SECONDS="${DB_HEALTH_TIMEOUT_SECONDS:-90}"
API_START_TIMEOUT_SECONDS="${API_START_TIMEOUT_SECONDS:-90}"
MONITOR_TITLE="${MONITOR_TITLE:-integration-deploy-check}"
MONITOR_URL="${MONITOR_URL:-https://example.com}"
MONITOR_EXPECTED_STATUS="${MONITOR_EXPECTED_STATUS:-200}"

compose() {
  docker compose --project-name "$COMPOSE_PROJECT_NAME" --env-file "$ENV_FILE" "$@"
}

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required to run the deployment integration check." >&2
  exit 127
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "docker compose is required to run the deployment integration check." >&2
  exit 127
fi

cleanup() {
  if [[ "${KEEP_COMPOSE_STACK:-0}" != "1" ]]; then
    compose down --volumes --remove-orphans >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

echo "Starting deployment stack with docker compose up --build..."
compose up --build -d

wait_for_db() {
  local deadline=$((SECONDS + DB_HEALTH_TIMEOUT_SECONDS))
  local db_container
  db_container="$(compose ps -q db)"

  if [[ -z "$db_container" ]]; then
    echo "db container was not created." >&2
    return 1
  fi

  until [[ "$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}missing{{end}}' "$db_container")" == "healthy" ]]; do
    if (( SECONDS >= deadline )); then
      echo "Timed out waiting for db to become healthy." >&2
      compose ps
      compose logs db
      return 1
    fi
    sleep 2
  done
}

wait_for_api_running() {
  local deadline=$((SECONDS + API_START_TIMEOUT_SECONDS))
  local api_container
  api_container="$(compose ps -q api)"

  if [[ -z "$api_container" ]]; then
    echo "api container was not created." >&2
    return 1
  fi

  until [[ "$(docker inspect --format '{{.State.Status}}' "$api_container")" == "running" ]]; do
    if [[ "$(docker inspect --format '{{.State.Status}}' "$api_container")" == "exited" ]]; then
      echo "api container exited before becoming ready." >&2
      compose logs api
      return 1
    fi
    if (( SECONDS >= deadline )); then
      echo "Timed out waiting for api container to run." >&2
      compose ps
      compose logs api
      return 1
    fi
    sleep 2
  done
}

wait_for_ready() {
  local deadline=$((SECONDS + READY_TIMEOUT_SECONDS))
  until python - "http://127.0.0.1:${APP_PORT}/ready" <<'PY'
import json
import sys
from urllib.request import urlopen

url = sys.argv[1]
with urlopen(url, timeout=2) as response:
    body = json.loads(response.read().decode())
if body != {"status": "ready"}:
    raise SystemExit(f"unexpected /ready response: {body!r}")
PY
  do
    if (( SECONDS >= deadline )); then
      echo "Timed out waiting for /ready to return {\"status\": \"ready\"}." >&2
      compose ps
      compose logs api
      return 1
    fi
    sleep 2
  done
}

create_and_verify_monitor() {
  local payload monitor_id persisted_count
  payload="$({
    printf '{'
    printf '"title":"%s",' "$MONITOR_TITLE"
    printf '"type":"http",'
    printf '"interval_seconds":60,'
    printf '"config":{"url":"%s","expected_status":%s}' "$MONITOR_URL" "$MONITOR_EXPECTED_STATUS"
    printf '}'
  })"

  monitor_id="$(python - "http://127.0.0.1:${APP_PORT}/monitor/" "$payload" <<'PY'
import json
import sys
from urllib.request import Request, urlopen

url, payload = sys.argv[1], sys.argv[2]
request = Request(
    url,
    data=payload.encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urlopen(request, timeout=5) as response:
    body = json.loads(response.read().decode())
if "id" not in body:
    raise SystemExit(f"monitor response did not include id: {body!r}")
print(body["id"])
PY
  )"

  persisted_count="$(compose exec -T db psql \
    -U "${POSTGRES_USER:-ops_user}" \
    -d "${POSTGRES_DB:-ops_sentinel}" \
    -tAc "SELECT COUNT(*) FROM monitor WHERE id = ${monitor_id};")"

  if [[ "$persisted_count" != "1" ]]; then
    echo "Expected monitor ${monitor_id} to persist in PostgreSQL, got count=${persisted_count}." >&2
    return 1
  fi
}

wait_for_db
echo "db is healthy."

wait_for_api_running
echo "api container is running."

echo "Confirming alembic upgrade head succeeds in api container..."
compose exec -T api alembic upgrade head

wait_for_ready
echo "/ready returned {\"status\": \"ready\"}."

create_and_verify_monitor
echo "Monitor persisted in PostgreSQL."

echo "Deployment integration check passed."
