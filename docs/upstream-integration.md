# Upstream Integration

This document lists the upstream SunFounder components we rely on and the exact commands we use to install them on the Raspberry Pi.

Sources
- SunFounder PiCrawler docs: https://docs.sunfounder.com/projects/pi-crawler/en/latest/
- SunFounder Robot HAT docs: https://docs.sunfounder.com/projects/robot-hat-v4/en/latest/
- SunFounder repositories:
  - https://github.com/sunfounder/robot-hat (use branch `v2.0`)
  - https://github.com/sunfounder/vilib (use branch `picamera2`)
  - https://github.com/sunfounder/picrawler (main repo)

Install commands (recommended)

1. Update the OS and install essentials

```sh
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3-pip python3-setuptools python3-venv i2c-tools libcamera-tools libatlas-base-dev libjpeg-dev alsa-utils
```

2. Robot HAT (branch v2.0)

```sh
cd ~
git clone -b v2.0 https://github.com/sunfounder/robot-hat.git
cd robot-hat
sudo python3 setup.py install
```

3. vilib (picamera2 branch) — camera/vision support

```sh
cd ~
git clone -b picamera2 https://github.com/sunfounder/vilib.git
cd vilib
sudo python3 install.py
```

4. picrawler

```sh
cd ~
git clone https://github.com/sunfounder/picrawler.git --depth 1
cd picrawler
sudo python3 setup.py install
```

5. Configure I2S audio (if using speaker)

```sh
cd ~/picrawler
sudo bash i2samp.sh
# follow prompts and reboot if requested
```

Notes
- Servo calibration and zeroing: follow https://docs.sunfounder.com/projects/pi-crawler/en/latest/servo_zeroing.html to avoid damaging servos.
- Licensing: SunFounder code is GPL-3.0; review license implications for redistribution or bundling.
- For Pi 5 compatibility, use the `picamera2`-compatible `vilib` and ensure `libcamera` and related packages are installed.
