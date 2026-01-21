# AI Agent (ai-agent)

Purpose
- Provide high-level reasoning, natural language interaction, and behavior selection. The AI agent coordinates navigation, vision, telemetry, and interaction agents.

Design
- Hybrid mode: primary model calls to OpenRouter (remote, higher capability), fallback to a lightweight local model for offline/low-latency tasks.
- Use OpenRouter SDK for API access; store API key in GitHub Secrets for CI and in device secure storage for runtime.
- Follow privacy rule: no raw camera frames uploaded unless operator consent is set in config.

Security
- Keep API keys in environment or secure files (use `~/.secrets/picrawler/openrouter.key` with proper permissions).
- Telemetry and transcripts are redacted for PII before upload.

Installation (initial)
1. Add `openrouter` SDK to the venv: `pip install openrouter` (or the official client recommended by OpenRouter docs).
2. Create a systemd unit `ai-agent.service` that runs `ai_agent.py` under the project's venv.
3. Add CI tests that mock OpenRouter responses and validate agent prompts and outputs.

Prompts & policies
- Store prompt templates in `docs/agents/prompts/ai/` with versioning.
- Enforce an "operator consent" flag for high-privacy operations (raw image upload, personal data sync).

Next steps
- Implement `ai_agent.py` scaffold with OpenRouter client usage, prompt templates, and a CLI to run locally in dev mode.
- Add tests that simulate OpenRouter replies and validate safety checks and PII redaction.
