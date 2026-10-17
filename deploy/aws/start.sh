#!/usr/bin/env bash
# Starts a stopped instance. Containers restart on their own (restart: unless-stopped); allow ~2 minutes.
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cloudshell_ready
need_state INSTANCE_ID SITE_HOST
aws_ ec2 start-instances --instance-ids "$(state_get INSTANCE_ID)" --query 'StartingInstances[0].CurrentState.Name' --output text
aws_ ec2 wait instance-running --instance-ids "$(state_get INSTANCE_ID)"
echo "Running. Give it about 2 minutes, then open https://$(state_get SITE_HOST)"
