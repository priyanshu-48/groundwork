#!/usr/bin/env bash
# Stores the app's secrets in SSM Parameter Store (SecureString, encrypted, free tier).
# - JWT_SECRET, ADMIN_TOKEN, POSTGRES_PASSWORD, SIGNUP_CODE are generated here, never shown except
#   the invite code at the end (you hand it to people you invite).
# - GEMINI_API_KEY is typed at a hidden prompt (nothing is echoed, nothing goes on a command line).
# Existing parameters are kept unless you answer yes to replacing them.
set -euo pipefail
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
require_cloudshell_ready
umask 077
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

exists() { aws_ ssm get-parameter --name "/$NAME/$1" >/dev/null 2>&1; }

put() { # put NAME TYPE  (value read from $tmp)
  aws_ ssm put-parameter --name "/$NAME/$1" --type "$2" --overwrite --value "file://$tmp" >/dev/null
  echo "stored /$NAME/$1"
}

generate() { # generate NAME BYTES
  if exists "$1"; then echo "/$NAME/$1 already exists, kept"; return; fi
  openssl rand -hex "$2" | tr -d '\n' >"$tmp"
  put "$1" SecureString
}

generate JWT_SECRET 32
generate ADMIN_TOKEN 16
generate POSTGRES_PASSWORD 16
generate SIGNUP_CODE 6

replace=yes
if exists GEMINI_API_KEY; then
  confirm "/$NAME/GEMINI_API_KEY already exists. Replace it?" && replace=yes || replace=no
fi
if [ "$replace" = yes ]; then
  read -r -s -p "Paste your Gemini API key (hidden), then press Enter: " key
  echo
  [ -n "$key" ] || die "no key entered"
  printf '%s' "$key" >"$tmp"
  unset key
  put GEMINI_API_KEY SecureString
fi

# Non-secret settings (plain String). Press Enter to accept the defaults shown.
read -r -p "Model fallback list, comma separated (Enter to skip): " models || models=""
if [ -n "$models" ]; then printf '%s' "$models" >"$tmp"; put GEMINI_MODELS String; fi
printf 'gemini' >"$tmp"; put AI_PROVIDER String

echo
echo "Invite code for signup (share it only with people you invite):"
aws_ ssm get-parameter --name "/$NAME/SIGNUP_CODE" --with-decryption --query Parameter.Value --output text
echo "Read it again any time with:  deploy/aws/show-secret.sh SIGNUP_CODE"
