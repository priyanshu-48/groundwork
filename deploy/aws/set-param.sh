#!/usr/bin/env bash
# Sets one setting in Parameter Store; it reaches the app on the next deploy (fetch-env.sh turns every
# parameter under /groundwork/ into an environment variable).
#   set-param.sh NAME VALUE          plain setting (shown in the console)
#   set-param.sh NAME --secret       hidden prompt, stored encrypted
#   set-param.sh NAME --delete       remove it (the app falls back to its default)
# Examples: EXTRACTION_ENABLED false | DEMO_ACCOUNT_EMAIL demo@example.com | DEMO_DAILY_CHAT_CAP 100
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cloudshell_ready
name="${1:?usage: set-param.sh NAME VALUE|--secret|--delete}"
value="${2:?usage: set-param.sh NAME VALUE|--secret|--delete}"
case "$name" in
  *[!A-Z0-9_]* | "") die "NAME must be UPPER_SNAKE_CASE" ;;
esac
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
umask 077
case "$value" in
  --delete)
    aws_ ssm delete-parameter --name "/$NAME/$name"
    echo "deleted /$NAME/$name"
    ;;
  --secret)
    read -r -s -p "Value for $name (hidden): " v
    echo
    [ -n "$v" ] || die "empty value"
    printf '%s' "$v" >"$tmp"
    unset v
    aws_ ssm put-parameter --name "/$NAME/$name" --type SecureString --overwrite --value "file://$tmp" >/dev/null
    echo "stored /$NAME/$name (encrypted)"
    ;;
  *)
    printf '%s' "$value" >"$tmp"
    aws_ ssm put-parameter --name "/$NAME/$name" --type String --overwrite --value "file://$tmp" >/dev/null
    echo "stored /$NAME/$name = $value"
    ;;
esac
echo "Takes effect on the next:  bash deploy/aws/04-deploy.sh"
