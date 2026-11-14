#!/usr/bin/env bash
# One-shot provisioner for the AI Computer stack on Ubuntu 24.04.
# Safe defaults: SSH kept, RDP not opened publicly, CDP localhost-only.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root: sudo $0 [--allow-rdp-from IP]" >&2
  exit 1
fi

ALLOW_ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --allow-rdp-from)
      ALLOW_ARGS=(--allow-rdp-from "${2:-}")
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

bash "${ROOT}/00-check-resources.sh"
bash "${ROOT}/01-install-desktop.sh"
bash "${ROOT}/02-install-chrome.sh"
bash "${ROOT}/03-install-xrdp.sh"
bash "${ROOT}/04-harden-firewall.sh" "${ALLOW_ARGS[@]}"
bash "${ROOT}/05-install-agent-runtime.sh"
bash "${ROOT}/06-install-codex.sh"

echo
echo "=== Bootstrap complete ==="
echo "1) Reconnect via SSH tunnel + RDP (see docs/setup.md)."
echo "2) Start Chrome:  aicomputer chrome start"
echo "3) Log into Instagram once in that Chrome window."
echo "4) Log into Codex: codex login  (ChatGPT Go — not API key)."
echo "5) Drop videos into ai_computer/media/inbox and run reels prepare."
