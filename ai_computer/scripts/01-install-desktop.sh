#!/usr/bin/env bash
# Install a light XFCE desktop on Ubuntu Server 24.04.
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root: sudo $0" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y \
  xfce4 \
  xfce4-terminal \
  xfce4-screenshooter \
  dbus-x11 \
  xorg \
  fonts-dejavu-core \
  fonts-noto-core \
  thunar \
  mousepad

# Prefer XFCE session for the invoking sudo user (or first non-root login user).
TARGET_USER="${SUDO_USER:-}"
if [[ -z "$TARGET_USER" || "$TARGET_USER" == "root" ]]; then
  TARGET_USER="$(logname 2>/dev/null || true)"
fi
if [[ -n "$TARGET_USER" && "$TARGET_USER" != "root" ]]; then
  HOME_DIR="$(getent passwd "$TARGET_USER" | cut -d: -f6)"
  sudo -u "$TARGET_USER" bash -c "echo xfce4-session > '${HOME_DIR}/.xsession'"
  echo "Wrote ${HOME_DIR}/.xsession for ${TARGET_USER}"
fi

echo "XFCE installed."
