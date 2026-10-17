#!/usr/bin/env bash
# Writes /opt/groundwork/runtime.env (mode 600) from the secret store: every AWS SSM parameter under
# /groundwork/ becomes KEY=value, the key being the parameter's last path segment (JWT_SECRET, ...).
# This is the one place that talks to the secret store. On Oracle, replace this script (Vault, or a
# root-only file you write by hand); nothing else changes.
set -euo pipefail
: "${AWS_REGION:?}" "${S3_BUCKET:?}" "${SITE_HOST:?}"
umask 077
tmp="$(mktemp /opt/groundwork/.runtime.env.XXXXXX)"
trap 'rm -f "$tmp"' EXIT
{
  echo "AWS_REGION=$AWS_REGION"
  echo "S3_BUCKET=$S3_BUCKET"
  echo "S3_REGION=$AWS_REGION"
  echo "SITE_HOST=$SITE_HOST"
  aws ssm get-parameters-by-path --region "$AWS_REGION" --path /groundwork/ --with-decryption \
    --query 'Parameters[].[Name,Value]' --output text |
    while IFS=$'\t' read -r name value; do
      printf '%s=%s\n' "${name##*/}" "$value"
    done
} >"$tmp"
mv "$tmp" /opt/groundwork/runtime.env
trap - EXIT
echo "runtime.env written ($(wc -l </opt/groundwork/runtime.env) lines; values not shown)"
