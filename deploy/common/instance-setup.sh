#!/usr/bin/env bash
# First-boot setup for a fresh Ubuntu 24.04 host (AWS user-data now, an Oracle VM later). Idempotent.
# Installs Docker, adds swap (image builds on a 2 GB host), and schedules the nightly DB backup.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

if ! command -v docker >/dev/null; then
  apt-get update -y
  apt-get install -y ca-certificates curl unzip cron
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    >/etc/apt/sources.list.d/docker.list
  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin docker-buildx-plugin
  systemctl enable --now docker
fi

if ! command -v aws >/dev/null; then
  # Official installer into /usr/local/bin (on PATH for SSM commands and cron, unlike a snap)
  case "$(uname -m)" in aarch64) arch=aarch64 ;; *) arch=x86_64 ;; esac
  tmp="$(mktemp -d)"
  curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-$arch.zip" -o "$tmp/awscli.zip"
  unzip -q "$tmp/awscli.zip" -d "$tmp"
  "$tmp/aws/install"
  rm -rf "$tmp"
fi

if ! swapon --show | grep -q /swapfile; then
  fallocate -l 2G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  grep -q /swapfile /etc/fstab || echo '/swapfile none swap sw 0 0' >>/etc/fstab
fi

mkdir -p /opt/groundwork/releases
chmod 700 /opt/groundwork

# Nightly dump to the bucket at 03:15 UTC. backup.sh reads /opt/groundwork/runtime.env.
# (release.sh rewrites this on every release, so it always matches the code on the host)
cat >/etc/cron.d/groundwork-backup <<'CRON'
15 3 * * * root bash /opt/groundwork/current/deploy/common/backup.sh >>/var/log/groundwork-backup.log 2>&1
CRON
chmod 644 /etc/cron.d/groundwork-backup
touch /opt/groundwork/.setup-done
