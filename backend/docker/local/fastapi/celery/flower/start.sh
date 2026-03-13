#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail


source .envs/.env.local 2>/dev/null || true

FLOWER_CMD="celery \
  -A backend.app.core.celery_app \
  -b ${CELERY_BROKER_URL:-amqp://guest:guest@rabbitmq:5672//} \
  flower \
  --address=0.0.0.0 \
  --port=5555 \
  --basic_auth=${CELERY_FLOWER_USER:-admin}:${CELERY_FLOWER_PASSWORD:-admin}"

exec watchfiles \
  --filter python \
  --ignore-paths '.envs:.git:__pycache__:*.pyc' \
  "$FLOWER_CMD"