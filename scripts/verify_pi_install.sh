#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT=${1:-/home/pi/picrawler_project}

echo "Verifying Raspberry Pi environment for PiCrawler..."

# Check OS
if [ -f /etc/os-release ]; then
  . /etc/os-release
  echo "OS: $NAME $VERSION"
else
  echo "No /etc/os-release found" >&2
fi

# Check required binaries
check_bin(){
  if command -v "$1" >/dev/null 2>&1; then
    echo "OK: $1 -> $(command -v $1)"
  else
    echo "MISSING: $1" >&2
  fi
}

bins=(git python3 pip3 i2cdetect libcamera-still)
for b in "${bins[@]}"; do
  check_bin "$b" || true
done

# Check config.txt for I2C/SPI
CONFIG_TXT=/boot/firmware/config.txt
if [ -f "$CONFIG_TXT" ]; then
  echo "Found config: $CONFIG_TXT"
  grep -E "dtparam=i2c|dtparam=spi" $CONFIG_TXT || echo "I2C/SPI not explicitly set in config.txt"
else
  echo "config.txt not found at $CONFIG_TXT" >&2
fi

# Check Python packages in venv (if exists)
if [ -d "$PROJECT_ROOT/venv" ]; then
  echo "Checking Python packages in virtualenv..."
  "$PROJECT_ROOT/venv/bin/pip" list --format=columns | sed -n '1,200p'
else
  echo "No virtualenv found at $PROJECT_ROOT/venv"
fi

# Check SunFounder packages presence
for d in robot-hat vilib picrawler; do
  if [ -d "$PROJECT_ROOT/$d" ]; then
    echo "Found $d at $PROJECT_ROOT/$d"
  else
    echo "Missing directory: $PROJECT_ROOT/$d" >&2
  fi
done

# Basic I2C scan
if command -v i2cdetect >/dev/null 2>&1; then
  echo "Running i2cdetect -y 1"
  i2cdetect -y 1 || true
else
  echo "i2cdetect not installed"
fi

# libcamera check
if command -v libcamera-still >/dev/null 2>&1; then
  echo "Listing cameras via libcamera-still"
  libcamera-still --list-cameras || true
else
  echo "libcamera-still not available"
fi

echo "Verification complete. Address any MISSING items before running autonomous behaviors."
