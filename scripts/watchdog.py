#!/usr/bin/env python3
"""Watchdog agent: polls metrics endpoint and evaluates rules, printing or executing enforcement actions.

This is a lightweight runtime that can be extended to actually call motor stop endpoints
or interact with systemd to restart agents.
"""
import time
import requests
import argparse
from prometheus_client.parser import text_string_to_metric_families
from scripts.rules_engine import RulesEngine


def fetch_metrics(url: str):
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    metrics = {}
    for family in text_string_to_metric_families(r.text):
        for m in family.samples:
            # only take unlabelled metrics (or the first) for now
            name = m.name
            val = m.value
            metrics[name] = val
    return metrics


def run_watchdog(metrics_url: str, interval: float = 5.0):
    engine = RulesEngine()
    while True:
        try:
            metrics = fetch_metrics(metrics_url)
            ts = time.time()
            actions = engine.evaluate_snapshot(metrics, ts=ts)
            for a in actions:
                print(f"[watchdog] Rule triggered: {a['rule_id']} -> actions: {a['actions']}")
                # TODO: implement enforcement hooks (stop motors, throttle, restart agent)
        except Exception as e:
            print(f"[watchdog] Error fetching metrics: {e}")
        time.sleep(interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--metrics-url', default='http://127.0.0.1:8000/metrics')
    parser.add_argument('--interval', type=float, default=5.0)
    args = parser.parse_args()

    run_watchdog(args.metrics_url, args.interval)
