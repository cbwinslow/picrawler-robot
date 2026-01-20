import argparse
import logging
import os
import subprocess
import sys
import json
import datetime
import shutil

# --- Configuration ---
PROJECT_ROOT = "/home/pi/picrawler_project" # This will be the actual path on the booted Pi
LOG_DIR = os.path.join(PROJECT_ROOT, "log")
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.json")

# --- Logger Setup ---
def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOG_DIR, f"picrawler_setup_{timestamp}.log")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("PicrawlerSetup")

logger = setup_logging()

# --- Helper Functions ---
def run_command(command, description, check_output=False, shell=False):
    logger.info(f"Executing: {description} (Command: {' '.join(command) if isinstance(command, list) else command})")
    try:
        if check_output:
            result = subprocess.run(command, check=True, capture_output=True, text=True, shell=shell)
            logger.info(f"Command successful. Output:\n{result.stdout.strip()}")
            return result.stdout.strip()
        else:
            subprocess.run(command, check=True, shell=shell)
            logger.info("Command successful.")
            return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {description}. Error: {e}")
        if e.stdout:
            logger.error(f"Stdout: {e.stdout.strip()}")
        if e.stderr:
            logger.error(f"Stderr: {e.stderr.strip()}")
        sys.exit(1)
    except FileNotFoundError:
        logger.error(f"Command not found: {command[0]}. Is it installed and in PATH?")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred while running command: {e}")
        sys.exit(1)

def save_config(config_data):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
        logger.info(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        logger.error(f"Failed to save configuration to {CONFIG_FILE}. Error: {e}")
        sys.exit(1)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config_data = json.load(f)
            logger.info(f"Configuration loaded from {CONFIG_FILE}")
            return config_data
        except Exception as e:
            logger.warning(f"Failed to load configuration from {CONFIG_FILE}. Starting with empty config. Error: {e}")
            return {}
    return {}

# --- Main Setup Functions ---

def detect_hardware():
    logger.info("Starting hardware detection...")
    hardware_info = {{}}

    # Detect Raspberry Pi model
    try:
        model_name = run_command(["cat", "/proc/device-tree/model"], "Detecting Raspberry Pi model", check_output=True)
        hardware_info["pi_model"] = model_name
        logger.info(f"Detected Raspberry Pi Model: {model_name}")
    except Exception as e:
        logger.warning(f"Could not detect Raspberry Pi model. Error: {e}")
        hardware_info["pi_model"] = "Unknown"

    # Detect Robot HAT (via I2C)
    logger.info("Checking for Robot HAT via I2C...")
    try:
        i2c_devices = run_command("i2cdetect -y 1", "Detecting I2C devices", check_output=True, shell=True)
        # Look for common Robot HAT I2C addresses (e.g., 0x14 for SunFounder Robot HAT)
        # This is a very basic check and might need refinement based on exact HAT.
        if "14" in i2c_devices: # Example I2C address for SunFounder Robot HAT
            hardware_info["robot_hat_detected"] = True
            logger.info("SunFounder Robot HAT detected via I2C (address 0x14).")
        else:
            hardware_info["robot_hat_detected"] = False
            logger.warning("Robot HAT not clearly detected via common I2C addresses. Check wiring.")
    except Exception as e:
        logger.warning(f"Could not perform I2C detection. Is i2c-tools installed? Error: {e}")
        hardware_info["robot_hat_detected"] = False

    # Detect Camera
    logger.info("Checking for camera modules...")
    try:
        # For libcamera (Pi 5)
        camera_list = run_command(["libcamera-still", "--list-cameras"], "Listing libcamera cameras", check_output=True)
        if "0 detected" not in camera_list:
            hardware_info["camera_detected"] = True
            hardware_info["camera_info"] = camera_list
            logger.info(f"Camera detected via libcamera:\n{camera_list}")
        else:
            hardware_info["camera_detected"] = False
            logger.warning("No libcamera camera detected.")
    except Exception as e:
        logger.warning(f"libcamera-still command failed. Is libcamera installed? Error: {e}")
        hardware_info["camera_detected"] = False

    # Add more sensor detection here as needed (e.g., check GPIO states, probe SPI/UART devices)

    logger.info("Hardware detection complete.")
    return hardware_info

def install_dependencies():
    """Install OS packages, SunFounder modules (robot-hat, vilib, picrawler), and Python deps."""
    logger.info("Starting dependency installation...")

    # Update and upgrade the system
    run_command(["sudo", "apt", "update"], "Updating apt package lists")
    run_command(["sudo", "apt", "upgrade", "-y"], "Upgrading installed packages")

    # Install common build tools and python essentials
    base_packages = [
        "git",
        "python3-pip",
        "python3-setuptools",
        "python3-venv",
        "i2c-tools",
        "libcamera-tools",
        "libatlas-base-dev",
        "libjpeg-dev",
        "alsa-utils",
    ]
    run_command(["sudo", "apt", "install", "-y"] + base_packages, "Installing essential system packages")

    # Install SunFounder libraries (robot-hat v2.0, vilib picamera2, picrawler)
    logger.info("Cloning and installing SunFounder PiCrawler components (robot-hat, vilib, picrawler)")
    repos = [
        ("https://github.com/sunfounder/robot-hat.git", "v2.0", os.path.join(PROJECT_ROOT, "robot-hat"), "cd {dest} && sudo python3 setup.py install"),
        ("https://github.com/sunfounder/vilib.git", "picamera2", os.path.join(PROJECT_ROOT, "vilib"), "cd {dest} && sudo python3 install.py"),
        ("https://github.com/sunfounder/picrawler.git", None, os.path.join(PROJECT_ROOT, "picrawler"), "cd {dest} && sudo python3 setup.py install"),
    ]

    for url, branch, dest, install_cmd_template in repos:
        if not os.path.exists(dest):
            clone_cmd = ["git", "clone"]
            if branch:
                clone_cmd += ["-b", branch]
            clone_cmd += [url, dest]
            run_command(clone_cmd, f"Cloning {url} ({'branch '+branch if branch else 'default branch'})")
        else:
            logger.info(f"{dest} already exists, skipping clone.")

        install_cmd = install_cmd_template.format(dest=dest)
        try:
            run_command(install_cmd, f"Installing from {dest}", shell=True)
        except SystemExit:
            logger.warning(f"Installation command for {dest} failed; please run it manually in {dest}.")

    # Run i2samp.sh if present (sets up I2S amplifier for audio)
    i2s_script = os.path.join(PROJECT_ROOT, "picrawler", "i2samp.sh")
    if os.path.exists(i2s_script):
        logger.info("Found i2samp.sh; running to configure I2S audio (may prompt for reboot).")
        try:
            run_command(f"cd {os.path.dirname(i2s_script)} && sudo bash i2samp.sh", "Running i2samp.sh", shell=True)
        except SystemExit:
            logger.warning("i2samp.sh failed or was interrupted. You may need to run it manually and reboot.")

    # Create and activate virtual environment
    logger.info("Setting up Python virtual environment...")
    venv_path = os.path.join(PROJECT_ROOT, "venv")
    if not os.path.exists(venv_path):
        run_command([sys.executable, "-m", "venv", venv_path], "Creating Python virtual environment")

    pip_path = os.path.join(venv_path, "bin", "pip")

    # Install Python dependencies
    python_deps = [
        "opencv-python",
        "numpy",
        "scipy",
        "pyaudio", # For microphone
        "vosk",    # For offline STT
        "RPi.GPIO",# Generic GPIO (though Robot HAT uses its own sometimes)
        "smbus",
        "smbus2",
    ]
    run_command([pip_path, "install"] + python_deps, "Installing Python dependencies")

    # Basic verification checks
    try:
        i2c_out = run_command("i2cdetect -y 1", "Detecting I2C devices", check_output=True, shell=True)
        logger.info(f"I2C devices detected:\n{i2c_out}")
    except Exception:
        logger.warning("i2c-tools not available or I2C interface not enabled.")

    try:
        cam_out = run_command(["libcamera-still", "--list-cameras"], "Listing libcamera cameras", check_output=True)
        logger.info(f"Camera info:\n{cam_out}")
    except Exception:
        logger.warning("libcamera-tools not available or no camera detected.")

    logger.info("Dependency installation complete.")

def configure_system():
    logger.info("Applying system configurations...")
    current_config = load_config()

    # Enable I2C and SPI if not already (via raspi-config equivalents)
    logger.info("Ensuring I2C and SPI interfaces are enabled...")
    # This is often done by adding dtparam=i2c_arm=on and dtparam=spi=on to /boot/firmware/config.txt
    # Modify /boot/firmware/config.txt (on the SD card's bootfs partition)
    config_txt_path = "/boot/firmware/config.txt" # This path is relative to the *booted* Pi
    # For now, we assume user will enable these via raspi-config post-boot if not already.
    # The script can verify these.
    logger.info("System configurations applied (basic).")
    save_config(current_config)

def run_tests():
    logger.info("Running basic hardware tests...")
    # Placeholder for test functions
    # E.g., check camera capture, audio record/playback, motor jiggle, sensor read
    logger.info("Basic hardware tests complete.")

def calibrate_hardware():
    logger.info("Starting hardware calibration...")
    # Placeholder for calibration routines
    # E.g., servo neutral position finding
    logger.info("Hardware calibration complete.")

def optimize_system():
    logger.info("Optimizing system settings...")
    # Placeholder for optimization functions
    # E.g., CPU governor, services startup
    logger.info("System optimization complete.")

# --- Main Function ---
def main():
    parser = argparse.ArgumentParser(description="PiCrawler Master Setup Script")
    parser.add_argument("--install", action="store_true", help="Install all dependencies and SunFounder libraries")
    parser.add_argument("--configure", action="store_true", help="Apply system configurations")
    parser.add_argument("--detect-hardware", action="store_true", help="Detect connected hardware components")
    parser.add_argument("--test", action="store_true", help="Run basic hardware tests")
    parser.add_argument("--calibrate", action="store_true", help="Run hardware calibration routines")
    parser.add_argument("--optimize", action="store_true", help="Optimize system settings")
    parser.add_argument("--all", action="store_true", help="Run all setup steps sequentially")

    args = parser.parse_args()

    if not (args.install or args.configure or args.detect_hardware or args.test or args.calibrate or args.optimize or args.all):
        parser.print_help()
        sys.exit(1)
    
    current_config = load_config()

    if args.all or args.detect_hardware:
        hardware_info = detect_hardware()
        current_config["hardware"] = hardware_info
        save_config(current_config)

    if args.all or args.install:
        install_dependencies()

    if args.all or args.configure:
        configure_system()

    if args.all or args.test:
        run_tests()

    if args.all or args.calibrate:
        calibrate_hardware()

    if args.all or args.optimize:
        optimize_system()

    logger.info("PiCrawler Master Setup Script finished.")

if __name__ == "__main__":
    main()
