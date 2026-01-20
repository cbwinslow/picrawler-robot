# Copilot / Agent Instructions

Purpose
- Provide guidance for automated agents (Copilot or other) operating on this repository.

Scope
- Agents may read and propose changes to documentation and scripts, open PRs, and run tests.
- Agents must not publish secrets or perform destructive operations on hardware without explicit human approval.

Safety
- Any change that affects hardware behavior (servo calibration, motor control, power) must include clear steps to stop motors and a safety checklist.

Development Workflow
- Use the `picrawler_setup.py` script to perform controlled installs and verifications.
- Run `scripts/verify_pi_install.sh` on the target Pi before running any autonomous behaviors.

Agent prompts
- Provide clear instructions for the agent with inputs required and expected output formats (see `docs/agents` for examples).
