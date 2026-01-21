# Remote Access & Cloudflare Tunnel (Quick Guide)

Use Case: securely expose local device endpoints (web UIs, telemetry APIs) to operators without opening inbound ports.

1. Install `cloudflared` on the Pi:
   - Download from Cloudflare and install the ARM64 package, or use their package repo.
2. Create a tunnel in Cloudflare for your account
   - `cloudflared tunnel create picrawler-001`
   - Note the generated credentials and attach to a DNS route (e.g., `picrawler.example.com`).
3. Run `cloudflared` as a daemon (systemd unit) that proxies local ports to the tunnel
   - Example service (simplified):
     - `cloudflared tunnel --url http://localhost:8080 run picrawler-001`
4. Security & Best practices
   - Restrict routes to specific paths and apply Cloudflare Access policies.
   - Use short-lived credentials and rotate them as part of device maintenance.
   - Ensure telemetry does not leak PII; use rule `privacy/no-raw-frame-upload` to guard uploads.

Notes:
- Cloudflare Tunnel uses outbound-only connections, so your device remains behind NAT/firewall without inbound rules.
- For operator push-notifications, use an authenticated webhook receiver behind the tunnel or an external service (PagerDuty, Slack, etc.).

See also: `docs/observability.md` (telemetry) and Cloudflare docs: https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/
