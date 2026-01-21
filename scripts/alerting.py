#!/usr/bin/env python3
"""Operator alerting via webhook with retries and simple rate limiting."""
import os
import time
import json
import logging
from typing import Dict

import requests

logger = logging.getLogger("alerting")
RATE_LIMIT_SECONDS = int(os.environ.get('PICRAWLER_ALERT_RATE_LIMIT', '10'))
LAST_ALERT_PATH = '/tmp/picrawler_last_alert'


def can_send_alert():
    try:
        if os.path.exists(LAST_ALERT_PATH):
            with open(LAST_ALERT_PATH, 'r') as f:
                last = float(f.read().strip())
            if time.time() - last < RATE_LIMIT_SECONDS:
                return False
    except Exception:
        logger.exception("Failed to read last alert timestamp")
    return True


def mark_alert_sent():
    try:
        with open(LAST_ALERT_PATH, 'w') as f:
            f.write(str(time.time()))
    except Exception:
        logger.exception("Failed to write last alert timestamp")


def send_alert(webhook_url: str, payload: Dict, retries: int = 3, backoff: float = 1.0) -> bool:
    if not can_send_alert():
        logger.info("Rate limit in effect; skipping alert")
        return False

    headers = {'Content-Type': 'application/json'}
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(webhook_url, json=payload, headers=headers, timeout=5)
            if r.status_code >= 200 and r.status_code < 300:
                logger.info("Alert sent successfully")
                mark_alert_sent()
                return True
            else:
                logger.warning("Alert failed with status %s: %s", r.status_code, r.text)
        except Exception as e:
            logger.exception("Attempt %d: exception when sending alert: %s", attempt, e)
        time.sleep(backoff * attempt)
    logger.error("All alert attempts failed")
    return False
