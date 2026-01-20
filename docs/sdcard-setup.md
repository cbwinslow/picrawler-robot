# SD Card Setup (Raspberry Pi 5)

Quick steps to prepare an SD card for PiCrawler on Raspberry Pi 5:

1. Flash Raspberry Pi OS (Bookworm 64-bit recommended) using Raspberry Pi Imager or `dd`.

2. Enable SSH and set initial Wi‑Fi (if headless):
   - For `ssh`, create an empty file named `ssh` in the boot partition.
   - Create `userconf` or `wpa_supplicant.conf` per Raspberry Pi docs.

3. Boot the Pi, login, and run setup script in this repo:

```sh
# on the Pi
git clone https://github.com/cbwinslow/picrawler-robot.git ~/picrawler_project
cd ~/picrawler_project
sudo python3 picrawler_setup.py --install
# or run individual steps
sudo python3 picrawler_setup.py --detect-hardware
```

4. Add autostart/systemd services for the main robot daemon (we will add a sample `systemd` unit in the repo).

5. For remote access during development, configure Cloudflare Tunnel and store credentials as GitHub Secrets for remote deployments.
