#!/usr/bin/env bash
# Deletes ONLY the resources listed in deploy/aws/state.env, asking before each group.
# Order matters: instance first (the security group cannot be deleted while it is in use).
set -uo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cloudshell_ready
[ -f "$STATE_FILE" ] || die "no $STATE_FILE: nothing recorded to delete"
echo "Recorded resources:"; sed 's/^/  /' "$STATE_FILE"; echo

IID="$(state_get INSTANCE_ID)"
if [ -n "$IID" ] && confirm "Terminate instance $IID (its disk is deleted too)?"; then
  aws_ ec2 terminate-instances --instance-ids "$IID" >/dev/null && aws_ ec2 wait instance-terminated --instance-ids "$IID"
  state_del INSTANCE_ID
fi

ALLOC="$(state_get ALLOCATION_ID)"
if [ -n "$ALLOC" ] && confirm "Release Elastic IP $(state_get PUBLIC_IP)? (stops its charge; the address is lost)"; then
  assoc="$(aws_ ec2 describe-addresses --allocation-ids "$ALLOC" --query 'Addresses[0].AssociationId' --output text 2>/dev/null)"
  [ -n "$assoc" ] && [ "$assoc" != None ] && aws_ ec2 disassociate-address --association-id "$assoc"
  aws_ ec2 release-address --allocation-id "$ALLOC" && { state_del ALLOCATION_ID; state_del PUBLIC_IP; state_del SITE_HOST; }
fi

SG="$(state_get SECURITY_GROUP)"
if [ -n "$SG" ] && confirm "Delete security group $SG?"; then
  for _ in $(seq 12); do aws_ ec2 delete-security-group --group-id "$SG" 2>/dev/null && { state_del SECURITY_GROUP; break; }; sleep 10; done
fi

ROLE="$(state_get ROLE)"
if [ -n "$ROLE" ] && confirm "Delete IAM role and instance profile $ROLE?"; then
  aws_ iam remove-role-from-instance-profile --instance-profile-name "$ROLE" --role-name "$ROLE" 2>/dev/null
  aws_ iam delete-instance-profile --instance-profile-name "$ROLE" 2>/dev/null
  aws_ iam detach-role-policy --role-name "$ROLE" --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore 2>/dev/null
  aws_ iam delete-role-policy --role-name "$ROLE" --policy-name "$NAME-app" 2>/dev/null
  aws_ iam delete-role --role-name "$ROLE" && { state_del ROLE; state_del INSTANCE_PROFILE; }
fi

if aws_ ssm get-parameters-by-path --path "/$NAME/" --query 'Parameters[].Name' --output text 2>/dev/null | grep -q .; then
  if confirm "Delete the stored secrets under /$NAME/ ?"; then
    aws_ ssm get-parameters-by-path --path "/$NAME/" --query 'Parameters[].Name' --output text | tr '\t' '\n' |
      while read -r p; do aws_ ssm delete-parameter --name "$p"; done
  fi
fi

BUCKET="$(state_get BUCKET)"
if [ -n "$BUCKET" ]; then
  echo "The bucket $BUCKET holds uploaded PDFs and database backups. Deleting it is permanent."
  if confirm "Empty and delete bucket $BUCKET?"; then
    aws_ s3 rm "s3://$BUCKET" --recursive --only-show-errors
    aws_ s3api delete-bucket --bucket "$BUCKET" && state_del BUCKET
  fi
fi
echo; echo "Remaining in $STATE_FILE:"; cat "$STATE_FILE" 2>/dev/null || true
