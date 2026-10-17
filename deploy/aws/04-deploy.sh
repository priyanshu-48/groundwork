#!/usr/bin/env bash
# Ships the code in this folder to the instance and starts (or updates) the stack.
#   ./deploy/aws/04-deploy.sh             build a bundle from this checkout, upload, release
#   ./deploy/aws/04-deploy.sh --rollback  switch back to the previous release
# No SSH and no registry: the bundle goes through the private bucket and the instance builds its own
# images; the command runs through Systems Manager. Re-runnable.
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cloudshell_ready
need_state BUCKET INSTANCE_ID SITE_HOST
BUCKET="$(state_get BUCKET)"
IID="$(state_get INSTANCE_ID)"
HOST="$(state_get SITE_HOST)"
aws_ ssm get-parameter --name "/$NAME/JWT_SECRET" >/dev/null 2>&1 || die "secrets missing: run 03-set-secrets.sh first"

if [ "${1:-}" = --rollback ]; then
  remote='bash /opt/groundwork/current/deploy/common/release.sh --rollback'
  confirm "Roll back to the previous release?" || die aborted
else
  stamp="$(date -u +%Y%m%d%H%M%S)"
  key="bundles/$NAME-$stamp.tgz"
  bundle="$(mktemp --suffix=.tgz)"
  tar -czf "$bundle" -C "$REPO_ROOT" --exclude=./deploy/aws/state.env --exclude=./.git \
    --exclude=./graphify-out --exclude=node_modules --exclude=.venv --exclude=./frontend/dist \
    --exclude=./.env --exclude=.flashrank --exclude=.coverage --exclude=__pycache__ \
    --exclude=.pytest_cache --exclude=.mypy_cache --exclude=.ruff_cache .
  echo "bundle: $(du -h "$bundle" | cut -f1)"
  confirm "Deploy to $HOST (instance $IID)?" || die aborted
  aws_ s3 cp "$bundle" "s3://$BUCKET/$key" --only-show-errors
  rel="$NAME-$stamp"
  remote="set -e
cloud-init status --wait || true
mkdir -p /opt/groundwork/releases/$rel
cat > /opt/groundwork/host.env <<'HOSTENV'
AWS_REGION=$REGION
S3_BUCKET=$BUCKET
SITE_HOST=$HOST
HOSTENV
aws s3 cp s3://$BUCKET/$key - --region $REGION --only-show-errors | tar -xz -C /opt/groundwork/releases/$rel
bash /opt/groundwork/releases/$rel/deploy/common/release.sh $key"
fi

params="$(mktemp)"
trap 'rm -f "${bundle:-}" "$params"' EXIT
REMOTE="$remote" python3 -c 'import json,os; print(json.dumps({"commands":[os.environ["REMOTE"]],"executionTimeout":["1800"]}))' >"$params"
cid="$(aws_ ssm send-command --instance-ids "$IID" --document-name AWS-RunShellScript \
  --parameters "file://$params" --timeout-seconds 1800 --comment "groundwork deploy" \
  --query Command.CommandId --output text)"
echo "command $cid sent; a first build takes about 5-10 minutes..."
while :; do
  status="$(aws_ ssm get-command-invocation --command-id "$cid" --instance-id "$IID" \
    --query Status --output text 2>/dev/null || echo Pending)"
  case "$status" in Pending | InProgress | Delayed) sleep 10 ;; *) break ;; esac
done
echo "---- output (tail) ----"
aws_ ssm get-command-invocation --command-id "$cid" --instance-id "$IID" --query StandardOutputContent --output text | tail -n 25
if [ "$status" != Success ]; then
  echo "---- errors ----"
  aws_ ssm get-command-invocation --command-id "$cid" --instance-id "$IID" --query StandardErrorContent --output text | tail -n 25
  die "deploy status: $status"
fi
echo
echo "Deployed. Open https://$HOST (the first request may take a few seconds while the certificate is issued)."
echo "Check it:  python3 deploy/common/smoke.py https://$HOST --code \$(deploy/aws/show-secret.sh SIGNUP_CODE)"
