#!/usr/bin/env bash
# READ-ONLY checks before anything is created. Safe to run any number of times.
# Run in AWS CloudShell (console, top bar, terminal icon) with the region set to Sydney.
set -uo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cloudshell_ready

echo "== Account and region"
echo "Account: $ACCOUNT_ID   Region used by these scripts: $REGION"
[ "${AWS_REGION:-${AWS_DEFAULT_REGION:-$REGION}}" = "$REGION" ] ||
  echo "NOTE: CloudShell is in ${AWS_REGION:-${AWS_DEFAULT_REGION}}; that is fine, every command here passes --region $REGION."

echo; echo "== Budget (a spend alarm should exist before creating anything)"
if budgets="$(aws budgets describe-budgets --account-id "$ACCOUNT_ID" --query 'Budgets[].[BudgetName,BudgetLimit.Amount]' --output text 2>&1)"; then
  [ -n "$budgets" ] && echo "$budgets" || echo "WARNING: no budgets found. Create one before continuing."
else
  echo "Could not list budgets ($budgets). Confirm in the console that your Zero-Spend budget exists."
fi

echo; echo "== Instance types this account can use for the Free plan ($REGION)"
free="$(aws_ ec2 describe-instance-types --filters Name=free-tier-eligible,Values=true \
  --query 'InstanceTypes[].InstanceType' --output text 2>&1)" || free=""
echo "${free:-(could not determine; the create script will fail safely if the type is not allowed)}"
case " $free " in
  *" $INSTANCE_TYPE "*) echo "OK: $INSTANCE_TYPE is eligible." ;;
  *) echo "WARNING: $INSTANCE_TYPE is not in the list above. Re-run with INSTANCE_TYPE=<a smaller arm64 type from the list, e.g. t4g.micro>." ;;
esac

echo; echo "== Ubuntu 24.04 arm64 image"
ami="$(aws_ ssm get-parameter --name /aws/service/canonical/ubuntu/server/24.04/stable/current/arm64/hvm/ebs-gp3/ami-id \
  --query Parameter.Value --output text 2>&1)" && echo "OK: $ami" || echo "WARNING: could not resolve the image: $ami"

echo; echo "== Network"
vpc="$(aws_ ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text 2>&1)"
[ "$vpc" != None ] && [ -n "$vpc" ] && echo "OK: default VPC $vpc" || echo "WARNING: no default VPC found"

echo; echo "== Already created by an earlier run?"
if [ -f "$STATE_FILE" ]; then sed 's/^/  /' "$STATE_FILE"; else echo "  nothing yet"; fi

echo; echo "== Estimated monthly cost if left running (Sydney, on-demand, approximate)"
cat <<'EOF'
  t4g.small compute  ~ $13      public IPv4 / Elastic IP ~ $3.7      20 GB gp3 disk ~ $2
  S3 + Parameter Store ~ $0     no NAT gateway, no RDS, no CloudFront, no CloudWatch logs
  Total ~ $19/month, drawn from your credits. Stop the instance when not demoing (scripts: stop.sh).
EOF
