#!/usr/bin/env bash
# Runs one shell command on the instance through Systems Manager (no SSH) and prints its output.
#   remote.sh "<command>"           waits until it finishes (up to 30 minutes)
# Handy ones:
#   remote.sh "bash /opt/groundwork/current/deploy/common/backup.sh"
#   remote.sh "cd /opt/groundwork/current && docker compose --env-file /opt/groundwork/runtime.env -f docker-compose.prod.yml exec -T api python -m app.worker.backfill_invoices"
# The command runs as root on the host. Do not put secrets in it (they would be stored in SSM history).
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cloudshell_ready
need_state INSTANCE_ID
IID="$(state_get INSTANCE_ID)"
cmd="${1:?usage: remote.sh \"<command>\"}"
params="$(mktemp)"
trap 'rm -f "$params"' EXIT
REMOTE="$cmd" python3 -c 'import json,os; print(json.dumps({"commands":[os.environ["REMOTE"]],"executionTimeout":["1800"]}))' >"$params"
cid="$(aws_ ssm send-command --instance-ids "$IID" --document-name AWS-RunShellScript \
  --parameters "file://$params" --timeout-seconds 1800 --comment "groundwork remote" \
  --query Command.CommandId --output text)"
echo "command $cid sent; waiting..."
while :; do
  status="$(aws_ ssm get-command-invocation --command-id "$cid" --instance-id "$IID" \
    --query Status --output text 2>/dev/null || echo Pending)"
  case "$status" in Pending | InProgress | Delayed) sleep 5 ;; *) break ;; esac
done
aws_ ssm get-command-invocation --command-id "$cid" --instance-id "$IID" --query StandardOutputContent --output text
errs="$(aws_ ssm get-command-invocation --command-id "$cid" --instance-id "$IID" --query StandardErrorContent --output text)"
[ -z "$errs" ] || { echo "---- stderr ----"; echo "$errs" | tail -n 20; }
echo "status: $status"
[ "$status" = Success ]
