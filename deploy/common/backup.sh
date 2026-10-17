#!/usr/bin/env bash
# Dump the database to the bucket (custom format, restorable with restore.sh). Run nightly by cron.
set -euo pipefail
ROOT=/opt/groundwork
set -a
. "$ROOT/runtime.env"
set +a
cd "$ROOT/current"
key="backups/groundwork-$(date -u +%Y%m%dT%H%M%SZ).dump"
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
docker compose --env-file "$ROOT/runtime.env" -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U groundwork -Fc groundwork >"$tmp"
[ -s "$tmp" ] || { echo "backup is empty, not uploading" >&2; exit 1; }
aws s3 cp "$tmp" "s3://$S3_BUCKET/$key" ${S3_ENDPOINT_URL:+--endpoint-url "$S3_ENDPOINT_URL"} --only-show-errors
echo "backup ok: $key ($(wc -c <"$tmp") bytes)"
