#!/usr/bin/env bash
# Prints one of the secrets you need to hand out or use yourself. Deliberately limited to two names.
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
case "${1:-}" in
  SIGNUP_CODE | ADMIN_TOKEN) ;;
  *) die "usage: show-secret.sh SIGNUP_CODE|ADMIN_TOKEN" ;;
esac
aws_ ssm get-parameter --name "/$NAME/$1" --with-decryption --query Parameter.Value --output text
