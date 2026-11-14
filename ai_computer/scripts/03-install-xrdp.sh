#!/usr/bin/env bash
# Install xrdp and wire it to XFCE.
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root: sudo $0" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y xrdp

adduser xrdp ssl-cert >/dev/null 2>&1 || true

TARGET_USER="${SUDO_USER:-}"
if [[ -z "$TARGET_USER" || "$TARGET_USER" == "root" ]]; then
  TARGET_USER="$(logname 2>/dev/null || true)"
fi
if [[ -n "$TARGET_USER" && "$TARGET_USER" != "root" ]]; then
  HOME_DIR="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
  sudo -u "$TARGET_USER" bash -c "echo xfce4-session > '${HOME_DIR}/.xsession'"
  # startwm.sh fallback for some xrdp builds
  if [[ -f /etc/xrdp/startwm.sh ]]; then
    if ! grep -q 'xfce4-session' /etc/xrdp/startwm.sh; then
      sed -i 's|^test -x /etc/X11/Xsession|# &|' /etc/xrdp/startwm.sh || true
      sed -i 's|^exec /bin/sh /etc/X11/Xsession|# &|' /etc/xrdp/startwm.sh || true
      if ! grep -q 'startxfce4\|xfce4-session' /etc/xrdp/startwm.sh; then
        printf '\nstartxfce4\n' >> /etc/xrdp/startwm.sh
      fi
    fi
  fi
fi

systemctl enable xrdp
systemctl restart xrdp

echo "xrdp listening (should be 3389):"
ss -lntp | grep -E ':3389\b' || true
echo
echo "Prefer connecting via SSH tunnel (do not expose 3389 publicly):"
echo "  ssh -N -L 3389:127.0.0.1:3389 USER@VPS"
echo "  then RDP to 127.0.0.1:3389"
