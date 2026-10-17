#!/usr/bin/env bash
# Stops the instance (no compute charge). The Elastic IP and disk keep costing a little (~$6/month
# together) and the address and data are kept. The stack comes back by itself on start.sh.
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cloudshell_ready
need_state INSTANCE_ID
confirm "Stop instance $(state_get INSTANCE_ID)? The site goes offline." || die aborted
aws_ ec2 stop-instances --instance-ids "$(state_get INSTANCE_ID)" --query 'StoppingInstances[0].CurrentState.Name' --output text
