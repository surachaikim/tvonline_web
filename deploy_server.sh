#!/usr/bin/env bash
set -euo pipefail

APP_NAME="tvhub-online"
IMAGE_TAG="tvhub-online:2026-06-15"
IMAGE_TAR="${1:-tvhub-online_2026-06-15.tar}"
ENV_FILE="${ENV_FILE:-.env.production}"
HOST_PORT="${HOST_PORT:-5000}"
CONTAINER_PORT="5000"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker command not found. Please install Docker first." >&2
  exit 1
fi

if [ ! -f "$IMAGE_TAR" ]; then
  echo "ERROR: image tar not found: $IMAGE_TAR" >&2
  echo "Usage: ./deploy_server.sh /path/to/tvhub-online_2026-06-15.tar" >&2
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  cat > "$ENV_FILE.example" <<'EOF'
FLASK_SECRET_KEY=change-this-secret
ADMIN_PASSWORD=change-this-admin-password
SITE_NAME=TVHUB.ONLINE
BASE_URL=https://tvhub.online
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=tvhub
DB_PASS=change-this-db-password
DB_NAME=tvhub
GEMINI_API_KEY=
EOF
  echo "ERROR: env file not found: $ENV_FILE" >&2
  echo "Created template: $ENV_FILE.example" >&2
  echo "Copy it to $ENV_FILE, edit values, then run this script again." >&2
  exit 1
fi

echo "Loading Docker image from $IMAGE_TAR ..."
docker load -i "$IMAGE_TAR"

echo "Stopping old container if exists ..."
docker rm -f "$APP_NAME" >/dev/null 2>&1 || true

echo "Starting $APP_NAME on port $HOST_PORT ..."
docker run -d \
  --name "$APP_NAME" \
  --env-file "$ENV_FILE" \
  -p "$HOST_PORT:$CONTAINER_PORT" \
  -v "$(pwd)/channel_clicks.json:/app/channel_clicks.json" \
  --restart unless-stopped \
  "$IMAGE_TAG"

echo "Waiting for app to respond ..."
for i in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:$HOST_PORT/" >/dev/null 2>&1; then
    echo "Deploy complete: http://127.0.0.1:$HOST_PORT/"
    docker ps --filter "name=$APP_NAME" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
    exit 0
  fi
  sleep 2
done

echo "WARNING: container started but health check did not pass yet." >&2
echo "Recent logs:" >&2
docker logs --tail 80 "$APP_NAME" >&2
exit 1
