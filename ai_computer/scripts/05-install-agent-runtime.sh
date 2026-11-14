#!/usr/bin/env bash
# Install Python runtime + Playwright for the aicomputer CLI.
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root: sudo $0" >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_USER="${SUDO_USER:-}"
if [[ -z "$TARGET_USER" || "$TARGET_USER" == "root" ]]; then
  TARGET_USER="$(logname 2>/dev/null || true)"
fi
if [[ -z "$TARGET_USER" || "$TARGET_USER" == "root" ]]; then
  echo "Could not determine non-root target user." >&2
  exit 1
fi
HOME_DIR="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
VENV="${HOME_DIR}/.aicomputer/venv"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3 python3-venv python3-pip

install -d -o "$TARGET_USER" -g "$TARGET_USER" "${HOME_DIR}/.aicomputer" \
  "${HOME_DIR}/.aicomputer/state" \
  "${HOME_DIR}/.aicomputer/screenshots" \
  "${HOME_DIR}/.aicomputer/logs" \
  "${HOME_DIR}/.aicomputer/chrome-profile"

sudo -u "$TARGET_USER" python3 -m venv "$VENV"
sudo -u "$TARGET_USER" "$VENV/bin/pip" install --upgrade pip
sudo -u "$TARGET_USER" "$VENV/bin/pip" install -r "${ROOT}/agent/requirements.txt"

# Playwright browsers are NOT required when attaching to system Chrome via CDP.
# Still install the Python package deps only.
BIN_LINK="${HOME_DIR}/.local/bin/aicomputer"
install -d -o "$TARGET_USER" -g "$TARGET_USER" "${HOME_DIR}/.local/bin"
cat >"$BIN_LINK" <<EOF
#!/usr/bin/env bash
exec "${VENV}/bin/aicomputer" "\$@"
EOF
chown "$TARGET_USER:$TARGET_USER" "$BIN_LINK"
chmod +x "$BIN_LINK"

# Editable install of the package
sudo -u "$TARGET_USER" "$VENV/bin/pip" install -e "${ROOT}/agent"

echo "Installed aicomputer for ${TARGET_USER}."
echo "Ensure ~/.local/bin is on PATH, then run: aicomputer doctor"
