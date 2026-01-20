#!/usr/bin/env python3
"""Lightweight Prometheus exporter for PiCrawler system metrics.

Exports:
- picrawler_process_cpu_percent
- picrawler_process_memory_bytes
- picrawler_cpu_temp_celsius
- picrawler_uptime_seconds
- picrawler_last_heartbeat_timestamp
- picrawler_camera_frames_total
- picrawler_battery_voltage_volts (if robot-hat available)
- picrawler_servos_position_degrees (labels: servo)

Run:
  python3 scripts/metrics_exporter.py --port 8000

"""
from prometheus_client import start_http_server, Gauge, Counter
import time
import argparse
import os
import psutil

# Metrics
PROCESS_CPU = Gauge("picrawler_process_cpu_percent", "CPU percent used by picrawler process")
PROCESS_MEM = Gauge("picrawler_process_memory_bytes", "Memory used by picrawler process in bytes")
CPU_TEMP = Gauge("picrawler_cpu_temp_celsius", "CPU temperature in Celsius")
UPTIME = Gauge("picrawler_uptime_seconds", "System uptime in seconds")
LAST_HEARTBEAT = Gauge("picrawler_last_heartbeat_timestamp", "UTC timestamp of last heartbeat")
CAMERA_FRAMES = Counter("picrawler_camera_frames_total", "Total camera frames processed")
BATTERY_VOLT = Gauge("picrawler_battery_voltage_volts", "Battery voltage reported by Robot HAT", unit="volts")
SERVO_POS = Gauge("picrawler_servos_position_degrees", "Servo position in degrees", ['servo'])

# Try to import robot_hat utilities if available to read battery etc
robot_hat_utils = None
try:
    import robot_hat.utils as rh_utils
    robot_hat_utils = rh_utils
except Exception:
    robot_hat_utils = None

start_time = time.time()


def read_cpu_temp():
    # Common sysfs thermal path
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            t = int(f.read().strip()) / 1000.0
            return t
    except Exception:
        return None


def read_battery_voltage():
    if robot_hat_utils is None:
        return None
    try:
        return float(robot_hat_utils.get_battery_voltage())
    except Exception:
        return None


def update_metrics():
    p = psutil.Process(os.getpid())

    PROCESS_CPU.set(p.cpu_percent(interval=None))
    PROCESS_MEM.set(p.memory_info().rss)

    t = read_cpu_temp()
    if t is not None:
        CPU_TEMP.set(t)

    UPTIME.set(time.time() - start_time)
    LAST_HEARTBEAT.set(time.time())

    # battery
    bv = read_battery_voltage()
    if bv is not None:
        BATTERY_VOLT.set(bv)

    # servo placeholders (user code should set specific servo gauge values via /metrics push or local API)
    # Example static values for now
    SERVO_POS.labels(servo="servo0").set(0)
    SERVO_POS.labels(servo="servo1").set(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=int(os.environ.get("METRICS_PORT", 8000)))
    parser.add_argument("--interval", type=float, default=5.0, help="metrics update interval seconds")
    args = parser.parse_args()

    start_http_server(args.port)
    print(f"Metrics exporter running on :{args.port}")

    # Warm-up psutil cpu_percent
    psutil.cpu_percent(interval=None)

    try:
        while True:
            update_metrics()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Exporter stopped")
