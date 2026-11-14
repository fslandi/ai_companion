#!/usr/bin/env bash
# UFW baseline: keep SSH, do not publish Chrome CDP, optionally lock RDP.
#
# Usage:
#   sudo ./04-harden-firewall.sh                  # SSH only; RDP via tunnel
#   sudo ./04-harden-firewall.sh --allow-rdp-from 203.0.113.10
#   sudo CLIENT_IP=203.0.113.10 ./04-harden-firewall.sh --allow-rdp-from-env
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root: sudo $0" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ufw

ALLOW_RDP_FROM=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --allow-rdp-from)
      ALLOW_RDP_FROM="${2:-}"
      shift 2
      ;;
    --allow-rdp-from-env)
      ALLOW_RDP_FROM="${CLIENT_IP:-}"
      shift
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

# Never disrupt SSH mid-session.
ufw allow OpenSSH
ufw default deny incoming
ufw default allow outgoing

# Explicitly refuse common accidental exposures (even if something later binds them).
ufw deny 9222/tcp comment 'Chrome CDP must stay localhost'
ufw deny 5900/tcp comment 'VNC not used in v1'
ufw deny 6080/tcp comment 'noVNC not used in v1'

if [[ -n "$ALLOW_RDP_FROM" ]]; then
  ufw allow from "$ALLOW_RDP_FROM" to any port 3389 proto tcp comment 'xrdp from owner IP'
  echo "RDP allowed only from ${ALLOW_RDP_FROM}"
else
  # Prefer SSH tunnel; do not open 3389 to the world.
  ufw delete allow 3389/tcp >/dev/null 2>&1 || true
  echo "RDP left closed on public interfaces. Use SSH tunnel to 127.0.0.1:3389."
fi

ufw --force enable
ufw status verbose

echo
echo "Chrome DevTools (9222) must remain bound to 127.0.0.1 — see chrome/launch-chrome.sh"
