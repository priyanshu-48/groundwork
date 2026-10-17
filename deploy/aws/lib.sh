#!/usr/bin/env bash
# Shared helpers for the deploy/aws scripts. Meant to be sourced, not run.
# These scripts are written to run in AWS CloudShell (already signed in as you; no access keys).
# Every AWS call names the region explicitly, so nothing can land in the wrong one by accident.

# shellcheck disable=SC2034  # variables are used by the scripts that source this file
REGION=ap-southeast-2
NAME=groundwork
INSTANCE_TYPE="${INSTANCE_TYPE:-t4g.small}"
DISK_GB=20
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../.." && pwd)"
STATE_FILE="$HERE/state.env" # git-ignored: lists every resource these scripts created

die() { echo "ERROR: $*" >&2; exit 1; }

aws_() { aws --region "$REGION" "$@"; }

confirm() { # confirm "question"  -> returns 0 only for a typed yes
  local ans
  read -r -p "$1 [type 'yes' to continue]: " ans
  [ "$ans" = yes ]
}

state_get() { # state_get KEY -> value or empty
  [ -f "$STATE_FILE" ] || return 0
  grep -E "^$1=" "$STATE_FILE" | tail -1 | cut -d= -f2- || true
}

state_set() { # state_set KEY VALUE (written immediately, so a failure halfway still records what exists)
  touch "$STATE_FILE"
  chmod 600 "$STATE_FILE"
  grep -vE "^$1=" "$STATE_FILE" >"$STATE_FILE.tmp" || true
  echo "$1=$2" >>"$STATE_FILE.tmp"
  mv "$STATE_FILE.tmp" "$STATE_FILE"
}

state_del() {
  [ -f "$STATE_FILE" ] || return 0
  grep -vE "^$1=" "$STATE_FILE" >"$STATE_FILE.tmp" || true
  mv "$STATE_FILE.tmp" "$STATE_FILE"
}

require_cloudshell_ready() {
  command -v aws >/dev/null || die "the aws CLI is not available (run this in AWS CloudShell)"
  local acct
  acct="$(aws_ sts get-caller-identity --query Account --output text 2>/dev/null)" ||
    die "not signed in: run this in AWS CloudShell from the console"
  ACCOUNT_ID="$acct"
}

need_state() { # need_state KEY... -> die if any is missing (a previous script has not run)
  local k
  for k in "$@"; do
    [ -n "$(state_get "$k")" ] || die "$k is missing from $STATE_FILE: run the earlier scripts first"
  done
}
