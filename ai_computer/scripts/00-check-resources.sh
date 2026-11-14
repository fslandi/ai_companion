#!/usr/bin/env bash
# Print VPS resources so sizing decisions are based on facts, not guesses.
set -euo pipefail

echo "=== AI Computer resource check ==="
echo
echo "-- OS --"
if [[ -f /etc/os-release ]]; then
  # shellcheck disable=SC1091
  . /etc/os-release
  echo "NAME=${NAME:-unknown}"
  echo "VERSION=${VERSION:-unknown}"
else
  uname -a
fi

echo
echo "-- CPU --"
nproc
lscpu 2>/dev/null | awk -F: '/^Model name|^CPU\(s\)|^Thread|^Core|^Socket/ {gsub(/^[ \t]+/, "", $2); print $1": "$2}'

echo
echo "-- Memory --"
free -h

echo
echo "-- Disk --"
df -h / /home 2>/dev/null || df -h /

echo
echo "-- Swap --"
swapon --show || true
free -h | awk '/Swap/ {print}'

echo
echo "-- Recommendation (heuristic) --"
mem_mb="$(free -m | awk '/Mem:/ {print $2}')"
if (( mem_mb < 1800 )); then
  echo "RAM ~${mem_mb}MiB: add 2G swap before XFCE+Chrome; prefer 2GB+ RAM."
elif (( mem_mb < 3600 )); then
  echo "RAM ~${mem_mb}MiB: OK for XFCE+Chrome with 1–2 tabs; keep swap ready."
else
  echo "RAM ~${mem_mb}MiB: comfortable for desktop + Chrome + Codex."
fi
