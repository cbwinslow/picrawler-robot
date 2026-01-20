# Agents

This directory will contain prompts, agents definitions, and tooling for autonomous behaviors.

Planned agents:
- navigation-agent.md — waypoint navigation, obstacle avoidance
- vision-agent.md — object detection, face recognition
- telemetry-agent.md — periodic health and telemetry uploads (via Cloudflare Tunnel)
- watchdog-agent.md — safety watchdog to stop motors on critical events

Each agent will include:
- A short role description
- Input sources and expected formats (camera, imu, odometry)
- Example prompts and minimal output schema
