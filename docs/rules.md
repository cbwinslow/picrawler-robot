# Rules & Governance

Purpose

This file enumerates policy rules that govern the robot's behavior, safety constraints, telemetry policy, and agent-level restrictions. Rules are grouped so they can be enforced programmatically and tested.

Rule groups

- Safety rules (critical): immediate stop on hazardous conditions, physical safety, power thresholds.
- Operational rules (high): acceptable operating ranges, maintenance windows, battery/charge policies.
- Privacy & Data rules (high): do not transmit raw camera frames off-device without explicit consent; mask PII in telemetry.
- Telemetry & Observability rules (medium): metrics retention and sampling policies, telemetry frequency limits.
- Agent behavior rules (medium): action rate limiting, request confirmation for risky actions, human-in-the-loop thresholds.

Example rules (starter set)

1. safety/battery-low
   - severity: critical
   - description: If battery voltage < 6.0V for 15s, stop motors and signal emergency.
   - enforcement: immediate stop + persistent alert

2. safety/overtemp
   - severity: critical
   - description: If CPU temperature > 85C, reduce performance and notify operator.
   - enforcement: throttle CPU-bound tasks; stop movement if temp > 90C.

3. privacy/no-raw-frame-upload
   - severity: high
   - description: Raw camera frames must not be uploaded off-device unless explicitly enabled by a config toggle.
   - enforcement: telemetry-agent must redact or downsample frames per policy; require operator consent flag.

4. observability/heartbeat
   - severity: medium
   - description: Every critical agent must emit a heartbeat every 30s; missing heartbeat for 90s triggers an alert.
   - enforcement: watchdog-agent monitors heartbeats and raises issues.

Rule structure

Rules will be represented as YAML files under `config/rules/` with fields:
- id
- severity
- description
- trigger (metric or event condition)
- enforcement_action (stop, throttle, alert)
- tests (how to validate rule)

Next steps

- Add rule YAMLs under `config/rules/` and a basic validator test that ensures each rule has required fields.
- Integrate rule checks into the watchdog-agent for runtime enforcement.
