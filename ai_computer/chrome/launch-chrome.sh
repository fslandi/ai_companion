#!/usr/bin/env bash
# Launch Google Chrome with a persistent profile and CDP bound to localhost only.
set -euo pipefail

AICOMPUTER_HOME="${AICOMPUTER_HOME:-${HOME}/.aicomputer}"
PROFILE_DIR="${CHROME_PROFILE_DIR:-${AICOMPUTER_HOME}/chrome-profile}"
CDP_PORT="${CHROME_CDP_PORT:-9222}"
CDP_HOST="${CHROME_CDP_HOST:-127.0.0.1}"

if [[ "$CDP_HOST" != "127.0.0.1" && "$CDP_HOST" != "localhost" ]]; then
  echo "Refusing non-localhost CDP host: ${CDP_HOST}" >&2
  echo "Chrome DevTools must not be exposed to the network." >&2
  exit 1
fi

mkdir -p "$PROFILE_DIR" "${AICOMPUTER_HOME}/logs"

CHROME_BIN=""
for candidate in google-chrome-stable google-chrome chromium-browser chromium; do
  if command -v "$candidate" >/dev/null 2>&1; then
    CHROME_BIN="$(command -v "$candidate")"
    break
  fi
done
if [[ -z "$CHROME_BIN" ]]; then
  echo "Chrome/Chromium not found on PATH." >&2
  exit 1
fi

# If DISPLAY is unset, try common desktop display.
if [[ -z "${DISPLAY:-}" ]]; then
  export DISPLAY="${AICOMPUTER_DISPLAY:-:10.0}"
fi

# Avoid starting a second instance that would fight the profile lock.
if curl -fsS "http://${CDP_HOST}:${CDP_PORT}/json/version" >/dev/null 2>&1; then
  echo "Chrome CDP already available at http://${CDP_HOST}:${CDP_PORT}"
  curl -fsS "http://${CDP_HOST}:${CDP_PORT}/json/version"
  exit 0
fi

EXTRA_FLAGS=()
# Useful on some VPS GPUs / remote desktops
EXTRA_FLAGS+=(--disable-dev-shm-usage)
EXTRA_FLAGS+=(--no-first-run)
EXTRA_FLAGS+=(--no-default-browser-check)

nohup "$CHROME_BIN" \
  --user-data-dir="$PROFILE_DIR" \
  --remote-debugging-address="$CDP_HOST" \
  --remote-debugging-port="$CDP_PORT" \
  "${EXTRA_FLAGS[@]}" \
  "about:blank" \
  >>"${AICOMPUTER_HOME}/logs/chrome.log" 2>&1 &

for _ in $(seq 1 30); do
  if curl -fsS "http://${CDP_HOST}:${CDP_PORT}/json/version" >/dev/null 2>&1; then
    echo "Chrome started. CDP: http://${CDP_HOST}:${CDP_PORT}"
    curl -fsS "http://${CDP_HOST}:${CDP_PORT}/json/version"
    exit 0
  fi
  sleep 0.5
done

echo "Chrome did not open CDP in time. Check ${AICOMPUTER_HOME}/logs/chrome.log" >&2
exit 1
