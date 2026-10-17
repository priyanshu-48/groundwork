#!/usr/bin/env bash
# Restore a dump into the running database (replaces its contents). Usage: restore.sh <key|latest> [--yes]
# The API and worker are stopped during the restore and started again afterwards.
set -euo pipefail
ROOT=/opt/groundwork
set -a
. "$ROOT/runtime.env"
set +a
cd "$ROOT/current"
EP=${S3_ENDPOINT_URL:+--endpoint-url "$S3_ENDPOINT_URL"}
key="${1:?usage: restore.sh <key|latest> [--yes]}"
if [ "$key" = latest ]; then
  # shellcheck disable=SC2086
  key="$(aws s3 ls "s3://$S3_BUCKET/backups/" $EP | awk '{print $4}' | sort | tail -1)"
  key="backups/$key"
fi
echo "Restoring s3://$S3_BUCKET/$key into the live database. This REPLACES its contents."
if [ "${2:-}" != --yes ]; then
  read -r -p "Type 'restore' to continue: " ans
  [ "$ans" = restore ] || { echo aborted; exit 1; }
fi
dc() { docker compose --env-file "$ROOT/runtime.env" -f docker-compose.prod.yml "$@"; }
dc stop api worker
# shellcheck disable=SC2086
aws s3 cp "s3://$S3_BUCKET/$key" - $EP --only-show-errors |
  dc exec -T postgres pg_restore -U groundwork -d groundwork --clean --if-exists --no-owner
dc start api worker
echo "restore done"
