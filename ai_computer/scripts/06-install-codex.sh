#!/usr/bin/env bash
# Install Codex CLI for the desktop user. Auth via ChatGPT Go — not API key.
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root: sudo $0" >&2
  exit 1
fi

TARGET_USER="${SUDO_USER:-}"
if [[ -z "$TARGET_USER" || "$TARGET_USER" == "root" ]]; then
  TARGET_USER="$(logname 2>/dev/null || true)"
fi
if [[ -z "$TARGET_USER" || "$TARGET_USER" == "root" ]]; then
  echo "Could not determine non-root target user." >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y curl ca-certificates

# Official installer; runs as the target user so binaries land in their PATH.
sudo -u "$TARGET_USER" bash -lc 'curl -fsSL https://chatgpt.com/codex/install.sh | sh'

echo
echo "Codex CLI installed for ${TARGET_USER}."
echo "Next (as ${TARGET_USER}, preferably inside an RDP desktop session):"
echo "  codex login"
echo "Choose: Sign in with ChatGPT  (uses ChatGPT Go plan limits)."
echo "Do NOT pipe an OpenAI API key unless you explicitly want API billing."
