# Agents (Design & Catalog)

Purpose

This document defines the initial agent catalog, role responsibilities, input/output contracts, and grouping structure for PiCrawler's autonomous agents. Agents are modular programs (or prompts+tooling) that perform specific functions such as navigation, vision, telemetry, safety monitoring, and interaction.

Groups

- Navigation Agents
  - navigation-agent: waypoint planning, path-following, obstacle avoidance, publishes motor commands and nav status.
  - motion-planner-agent: responsible for low-level gait and step sequence optimization.

- Vision Agents
  - vision-agent: object detection, face recognition, labeling and localization of visual features.
  - camera-health-agent: monitors camera uptime and frame-drop metrics.

- Telemetry & Observability Agents
  - telemetry-agent: aggregates metrics/logs, uploads summaries via Cloudflare Tunnel, and performs periodic diagnostics snapshots.
  - metrics-exporter-agent: ensures `/metrics` endpoint health and labels.

- Safety & Watchdog Agents
  - watchdog-agent: monitors battery, current, temperature and raises emergency stop events.
  - collision-avoidance-agent: faststop for imminent collisions based on short-range sensors.

- Interaction Agents
  - speech-agent: TTS and STT orchestration, user intent classification.
  - personality-agent: high-level behavior selector (play, explore, avoid) based on mission rules.

Agent Contracts

Each agent must include
- `id`: unique agent identifier
- `description`: short summary
- `inputs`: sources (camera, imu, odometry, telemetry)
- `outputs`: event/actions (motor commands, stop, telemetry upload)
- `safety_level`: {critical, high, medium, low}
- `test_plan`: short description of tests that validate correctness

Prompts & Templates

We will keep prompt templates in `docs/agents/prompts/` and programmatic agent configs in `config/agents/` for reproducibility and validation.

Next steps

- Add initial YAML configs under `config/agents/` (navigation, vision, telemetry, watchdog).
- Implement a simple validation test to ensure all agent configs supply required fields.
