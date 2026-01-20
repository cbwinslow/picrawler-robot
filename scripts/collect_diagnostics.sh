#!/usr/bin/env bash
set -euo pipefail

OUTDIR=${1:-/tmp/picrawler-diagnostics}
mkdir -p "$OUTDIR"
TS=$(date -u +%Y%m%dT%H%M%SZ)

echo "Collecting diagnostics to $OUTDIR"

uname -a > "$OUTDIR/uname.txt" 2>&1
cat /etc/os-release > "$OUTDIR/os-release.txt" 2>&1 || true

echo "--- dmesg ---" > "$OUTDIR/dmesg.txt"
dmesg | tail -n 200 >> "$OUTDIR/dmesg.txt" 2>&1 || true

echo "--- journalctl (last 200 lines) ---" > "$OUTDIR/journalctl.txt"
journalctl -n 200 --no-pager >> "$OUTDIR/journalctl.txt" 2>&1 || true

if command -v i2cdetect >/dev/null 2>&1; then
  i2cdetect -y 1 > "$OUTDIR/i2cdetect.txt" 2>&1 || true
fi

if command -v libcamera-still >/dev/null 2>&1; then
  libcamera-still --list-cameras > "$OUTDIR/libcamera.txt" 2>&1 || true
fi

pip3 list --format=columns > "$OUTDIR/pip-list.txt" 2>&1 || true

# Files from project
if [ -d "/home/pi/picrawler_project" ]; then
  tar -czf "$OUTDIR/picrawler_project_files.tar.gz" -C /home/pi picrawler_project || true
fi

echo "Packaging diagnostics"
ARCHIVE="/tmp/picrawler-diagnostics-$TS.tar.gz"
 tar -czf "$ARCHIVE" -C "$(dirname "$OUTDIR")" "$(basename "$OUTDIR")"
 echo "Diagnostics saved to $ARCHIVE"
