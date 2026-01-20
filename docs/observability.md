# Observability & Telemetry (Design Requirements)

Goal: Provide comprehensive observability across the PiCrawler system: metrics (Prometheus), logs (structured, JSON where possible), traces (OpenTelemetry where feasible), telemetry uploads (via Cloudflare Tunnel), and dashboards/alerts (Grafana/Prometheus Alertmanager).

Principles
- Measure everything: CPU, memory, temperature, battery voltage, motor currents, servo positions, camera frames processed, network health, storage health, and process heartbeats.
- Use Prometheus metric naming best practices (metric_name{subsystem="..."}).
- Export a `/metrics` HTTP endpoint on the device for scraping.
- Logs: structured logs (JSON) written to `journald` and to rotating logs under `/var/log/picrawler/`.
- Traces: instrument long-running tasks (e.g., navigation decisions, CV pipeline) with OpenTelemetry spans when possible.
- Telemetry: periodic summaries pushed to a remote backend via Cloudflare Tunnel or via secure upload to S3-like bucket; respect privacy and do not leak secrets in telemetry.

Metrics schema (initial)
- picrawler_process_cpu_percent
- picrawler_process_memory_bytes
- picrawler_cpu_temp_celsius
- picrawler_uptime_seconds
- picrawler_last_heartbeat_timestamp
- picrawler_camera_frames_total
- picrawler_battery_voltage_volts
- picrawler_servos_position_degrees{servo}
- picrawler_motor_current_amps{motor}
- picrawler_nav_goal_distance_meters
- picrawler_vision_detections{label}

Scraping & dashboards
- Provide example Prometheus `scrape_configs` for the device (scrape targets via static config or via service discovery through the Cloudflare Tunnel).
- Create a Grafana dashboard skeleton for system overview: CPU/Temp, battery, servo status, camera throughput, nav status.

Alerts (examples)
- Battery voltage < 6.0V for 30s → critical alert
- CPU temp > 85C → critical alert
- No heartbeat for 60s → service check failure

Next steps
- Implement `scripts/metrics_exporter.py` and a systemd unit (done as scaffold).
- Add tests to validate `/metrics` responses and metrics presence.
- Add CI to run tests and to validate metrics formatting.
