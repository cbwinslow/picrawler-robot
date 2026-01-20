# Robot HAT (SunFounder)

Summary

The Robot HAT is an expansion board that provides motor drivers, PWM/servo expansion, ADC, speaker/I2S, and more. We rely on this board for motor control, battery monitoring, and audio output.

Key APIs (see upstream docs for full reference):
- `robot_hat.Motors` / `robot_hat.module.motor` — motor control
- `robot_hat.Servo` / `robot_hat.PWM` — servo control and PWM configuration
- `robot_hat.utils` — helpers for `get_ip()`, `set_volume()`, `get_battery_voltage()`
- `robot_hat.TTS` and `robot_hat.Music` — sound and TTS helpers

Best practices
- Install the `robot-hat` package from SunFounder (branch `v2.0`) and use their API for low-level interactions.
- Calibrate servos before first run (`servo_zeroing` guide in upstream docs).
- Carefully monitor battery voltage readings to avoid servo stalls or brownouts.
