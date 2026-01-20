# Safety and Calibration

Before powering servos or running autonomous behaviors, do the following:

1. Ensure a reliable power supply (recommend 6.0V-8.4V as per Robot HAT). Do not power servos from Pi's 5V rail alone.
2. Keep the robot elevated to avoid unexpected movement during calibration.
3. Run servo zeroing as described by SunFounder: https://docs.sunfounder.com/projects/pi-crawler/en/latest/servo_zeroing.html
4. Confirm wheel/motor directions with short test pulses and low power before enabling full speed.

Emergency stop
- Have a physical kill switch or keep a maintenance key to quickly disconnect battery.
