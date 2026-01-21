"""Enforcement helpers for actions returned by rules engine.

Functions are safe by default (dry-run) and attempt best-effort real enforcement
if the environment provides robot-hat or systemd controls. They should be
callable by the Watchdog agent.
"""
import subprocess
import logging
import os
from typing import List

logger = logging.getLogger("enforcement")


def stop_motors(dry_run: bool = True) -> bool:
    logger.info("Enforcement: stop_motors (dry_run=%s)", dry_run)
    if dry_run:
        return True
    # Try to use robot_hat API if available
    try:
        import robot_hat
        try:
            # try common API shapes
            if hasattr(robot_hat, 'Motors'):
                robot_hat.Motors().stop()
                logger.info("Motors stopped via robot_hat.Motors().stop()")
                return True
        except Exception:
            logger.exception("robot_hat present but failed to stop motors")
    except Exception:
        logger.debug("robot_hat not available; falling back to systemd stop")

    # Fallback: try to stop a known systemd service that controls motors
    try:
        subprocess.run(["systemctl", "stop", "picrawler.service"], check=True)
        logger.info("picrawler.service stopped via systemctl")
        return True
    except Exception:
        logger.exception("Failed to stop picrawler.service")
        return False


def throttle_cpu(dry_run: bool = True) -> bool:
    logger.info("Enforcement: throttle_cpu (dry_run=%s)", dry_run)
    if dry_run:
        return True
    # Best-effort: write a flag file that operator tools can read and act on.
    try:
        with open('/tmp/picrawler_throttle_enabled', 'w') as f:
            f.write('1')
        logger.info('Wrote /tmp/picrawler_throttle_enabled')
        return True
    except Exception:
        logger.exception('Failed to write throttle flag')
        return False


def alert_operator(message: str) -> bool:
    # Simple alert via log for now; can be extended to send email, webhook, or push notification
    logger.warning("ALERT OPERATOR: %s", message)
    return True


def attempt_restart_agent(agent_name: str, dry_run: bool = True) -> bool:
    logger.info("Enforcement: attempt_restart_agent(%s) (dry_run=%s)", agent_name, dry_run)
    if dry_run:
        return True
    try:
        subprocess.run(["systemctl", "restart", agent_name], check=True)
        logger.info("Restarted %s via systemctl", agent_name)
        return True
    except Exception:
        logger.exception("Failed to restart %s", agent_name)
        return False


ACTION_MAP = {
    'stop_motors': stop_motors,
    'throttle_cpu_tasks': throttle_cpu,
    'alert_operator': alert_operator,
    'attempt_restart_agent': attempt_restart_agent,
}


def perform_actions(actions: List[str], dry_run: bool = True):
    results = []
    for a in actions:
        # allow actions that are strings or dicts with params
        if isinstance(a, dict):
            name = list(a.keys())[0]
            val = a[name]
        else:
            name = a
            val = None
        handler = ACTION_MAP.get(name)
        if not handler:
            logger.warning("Unknown enforcement action: %s", name)
            results.append((name, False))
            continue
        try:
            if name == 'alert_operator':
                ok = handler(val if val else 'Alert from rules engine')
            elif name == 'attempt_restart_agent':
                ok = handler(val if val else 'picrawler.service', dry_run=dry_run)
            else:
                ok = handler(dry_run=dry_run)
            results.append((name, bool(ok)))
        except Exception:
            logger.exception("Error performing action: %s", name)
            results.append((name, False))
    return results
