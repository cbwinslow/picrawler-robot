# Project Rules & Governance

This document provides the top-down governance and operational rules that guide design, development, testing, deployment, and runtime behavior of the PiCrawler system.

## Vision & Mission 🎯
- Build an autonomous, safe, extensible, and auditable robot platform based on Raspberry Pi and SunFounder PiCrawler hardware.
- Prioritize safety, reproducibility, observability, privacy, and maintainability across all development phases.

## Principles
- **Safety-first:** automated actions affecting hardware must default to safe, reversible behavior.
- **Reproducibility:** third-party dependencies must be pinned and verified (`third_party/THIRD_PARTY_LOCK.json`).
- **Observability:** all subsystems export metrics, structured logs, and heartbeats.
- **Privacy:** PII and raw images are sensitive and governed by explicit consent flags.
- **Testability:** every rule and agent must include tests and CI verification where practical.

---

## Rule Groups (Top-level)
1. **Safety rules** (Severity: Critical) ✅
   - Immediate actions for hazardous conditions (stop motors, shut down). Examples: battery low, overheating, collision imminent.
2. **Operational rules** (Severity: High) ⚠️
   - Define operating ranges, maintenance, battery charge/discharge policies, and scheduled operations.
3. **Privacy & Data rules** (Severity: High) 🔒
   - Regulate capture, storage, transmission of camera frames, logs, and telemetry containing PII.
4. **Observability & Telemetry rules** (Severity: Medium) 📊
   - Metrics naming, cardinality limits, telemetry frequency, retention policies, and remote uploads.
5. **Agent behavior rules** (Severity: Medium) 🤖
   - Rate-limiting, approval requirements for risky actions, human-in-the-loop triggers.
6. **Security & Secrets rules** (Severity: High) 🔐
   - Keys/secrets must use GitHub Secrets for CI and on-device secure storage with least privilege.
7. **Development & Release rules** (Severity: Low) 🛠️
   - Branching, code-review, upstream contribution, and license compliance requirements.

---

## Rule Template
Every rule is represented as YAML under `config/rules/` with the following fields:

```yaml
id: <group>/<short-name>
severity: critical|high|medium|low
description: |
  <purpose and rationale>
trigger:
  metric: <metric_name>          # or event pattern
  condition: "> 85"            # operator and threshold
  duration_seconds: 10           # optional
enforcement_action:
  - stop_motors
  - alert_operator
tests:
  - simulate_metric: {metric: ..., values: [...], expected_action: ...}
```

Rules must include tests that validate triggers and enforcement behavior.

---

## Core Rules (starter set)
- **`safety/battery-low` (critical):** If `picrawler_battery_voltage_volts` < 6.0 for 15s, call `stop_motors` and `alert_operator`.
- **`safety/overtemp` (critical):** If `picrawler_cpu_temp_celsius` > 85 for 10s, call `throttle_cpu_tasks` and `alert_operator`; if > 90 then `stop_motors`.
- **`safety/collision-imminent` (critical):** Immediate stop if `ultrasonic_distance_m` < 0.1 or vision predicts imminent collision.
- **`privacy/no-raw-frame-upload` (high):** Raw camera frames must not be uploaded unless `operator_consent=true`; uploads must be redacted/downgraded.
- **`observability/heartbeat` (medium):** Agents marked `critical` must emit `picrawler_agent_heartbeat{agent="<id>"}` every 30s; missing for >90s triggers `attempt_restart_agent` and `alert_operator`.

---

## Enforcement & Testing
- The `watchdog` agent polls `/metrics` and evaluates YAML rules via `scripts/rules_engine.py`.
- Enforcement functions live in `scripts/enforcement.py` and are **dry-run** by default; `--enforce` enables real actions.
- Tests must simulate metrics and confirm enforcement actions are returned and executed in dry-run mode; hardware-in-the-loop tests are required for changes that interact with motors or power systems.

---

## Change Control & Audit
- Rule changes require a PR with: rule YAML, unit tests, risk & recovery notes, and CI validation.
- Safety-critical rule changes require one additional `safety-review` approver and a documented test plan.
- Update `third_party/THIRD_PARTY_LOCK.json` and `third_party/THIRD_PARTY_LICENSES.md` when upstream dependencies change.

**Future:** consider using Open Policy Agent (OPA) for complex policy decisioning (privacy, multi-metric rules, or multi-agent policies); current implementation keeps rules as YAML for simplicity and testability.

---

## Operational Playbooks
- **Emergency stop:** operator command or rule enforcement → `stop_motors` → snapshot logs → alert operator → await manual restart.
- **Overtemp:** throttle CPU → pause non-essential workloads → alert operator → schedule cooldown and diagnostics.
- **Lost connectivity:** switch to local fallback behaviors and begin periodic telemetry uploads until operator resumes control.

---

## Contacts & Roles
- **Maintainers:** see `MAINTAINERS` file in repo
- **Safety reviewer:** `@maintainer` (add more as team grows)

---

## Links
- `config/rules/` — YAML rule files
- `scripts/rules_engine.py` — rule evaluator
- `scripts/watchdog.py` — runtime watchdog
- `prometheus/rules/picrawler_alerts.yml` — example Prometheus alerting rules mirroring critical safety rules
- `docs/observability.md`, `docs/safety-and-calibration.md`
