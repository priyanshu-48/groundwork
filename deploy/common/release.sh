#!/usr/bin/env bash
# Runs ON the host (via SSM on AWS). Usage: release.sh <bundle-key>   or   release.sh --rollback
# Unpacks a release bundle from the bucket, refreshes secrets, builds and starts the stack, and waits
# for the API to be healthy. The previous release stays on disk so --rollback is quick.
set -euo pipefail
ROOT=/opt/groundwork
. "$ROOT/host.env"
export AWS_REGION S3_BUCKET SITE_HOST
EP=${S3_ENDPOINT_URL:+--endpoint-url "$S3_ENDPOINT_URL"}

if [ "${1:-}" = --rollback ]; then
  [ -L "$ROOT/previous" ] || { echo "no previous release" >&2; exit 1; }
  target="$(readlink -f "$ROOT/previous")"
  cur="$(readlink -f "$ROOT/current")"
  ln -sfn "$cur" "$ROOT/previous"
else
  key="${1:?usage: release.sh <bundle-key>|--rollback}"
  name="$(basename "$key" .tgz)"
  target="$ROOT/releases/$name"
  if [ ! -d "$target" ]; then
    mkdir -p "$target"
    # shellcheck disable=SC2086
    aws s3 cp "s3://$S3_BUCKET/$key" - $EP --only-show-errors | tar -xz -C "$target"
  fi
  if [ -L "$ROOT/current" ] && [ "$(readlink -f "$ROOT/current")" != "$target" ]; then
    ln -sfn "$(readlink -f "$ROOT/current")" "$ROOT/previous"
  fi
fi
ln -sfn "$target" "$ROOT/current"

bash "$ROOT/current/deploy/common/fetch-env.sh"
cd "$ROOT/current"
docker compose --env-file "$ROOT/runtime.env" -f docker-compose.prod.yml up -d --build --remove-orphans

echo "waiting for the API to become healthy..."
for _ in $(seq 60); do
  if docker compose --env-file "$ROOT/runtime.env" -f docker-compose.prod.yml ps api | grep -q healthy; then
    echo "release live: $(basename "$target")"
    # keep the three newest releases, drop dangling images
    # shellcheck disable=SC2012
    ls -1dt "$ROOT"/releases/*/ | tail -n +4 | xargs -r rm -rf
    docker image prune -f >/dev/null
    exit 0
  fi
  sleep 5
done
echo "API did not become healthy in 5 minutes; last logs:" >&2
docker compose --env-file "$ROOT/runtime.env" -f docker-compose.prod.yml logs --tail 40 api >&2
exit 1
