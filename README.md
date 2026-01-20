# PiCrawler Robot Project

This repository contains the code and documentation to run and extend the PiCrawler robot on Raspberry Pi 5.

## Quick start

1. Flash Raspberry Pi OS Bookworm (64-bit) to an SD card and boot your Pi.
2. Clone this repository on the Pi and run the master setup script:

```sh
git clone https://github.com/cbwinslow/picrawler-robot.git ~/picrawler_project
cd ~/picrawler_project
sudo python3 picrawler_setup.py --install
```

3. Run verification on the Pi:

```sh
bash scripts/verify_pi_install.sh ~/picrawler_project
```

4. Follow `docs/safety-and-calibration.md` and `docs/sdcard-setup.md` before enabling autonomous modes.

## What this repo does
- Automates installation of SunFounder components (`robot-hat`, `vilib`, `picrawler`) and Python deps.
- Provides verification scripts, docs for SD setup, CPU/glue scripts, and agent prompt scaffolding.
- Adds CI linting workflow and documentation skeleton for agents and Copilot instructions.

## Next steps
- Add systemd service for the robot daemon (scaffold added at `deploy/picrawler.service`)
- Implement and test autonomous agent prompts and telemetry (Cloudflare Tunnel integration)
- Add comprehensive observability: Prometheus exporter, metrics, telemetry uploads, and dashboards (see `docs/observability.md`)

## Development dependencies
- For running tests and metrics exporter locally: `pytest`, `requests`, `prometheus_client`, `psutil`.


## Dependencies (high level)
- Raspberry Pi 5
- SunFounder PiCrawler Kit (Robot HAT, USB Camera, servos)
- Raspberry Pi OS Bookworm (64-bit)
- Python 3
- OpenCV and audio/stt libs

For details see `docs/upstream-integration.md` and `copilot-instructions.md`.
