#!/usr/bin/env python3
"""Simple rules engine for PiCrawler.

Loads YAML rules from config/rules/*.yaml and evaluates them against metric snapshots.
This is intentionally small and testable; enforcement actions are returned for calling
code (e.g., watchdog-agent) to execute.
"""
from glob import glob
import yaml
import time
import operator
from typing import List, Dict, Any

OP_MAP = {
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne,
}


class Rule:
    def __init__(self, data: Dict[str, Any]):
        self.id = data['id']
        self.severity = data.get('severity', 'medium')
        self.description = data.get('description', '')
        self.trigger = data.get('trigger', {})
        self.enforcement_action = data.get('enforcement_action', [])
        self.duration = self.trigger.get('duration_seconds', 0)

    def match_metric(self, metric_name: str, value: float) -> bool:
        trig = self.trigger
        if 'metric' not in trig:
            return False
        if trig['metric'] != metric_name:
            return False
        cond = trig.get('condition')
        if not cond:
            return False
        # condition format: "< 6.0" or "> 85"
        parts = cond.strip().split()
        if len(parts) == 2:
            op_sym, threshold = parts
            op = OP_MAP.get(op_sym)
            if op is None:
                return False
            try:
                thr = float(threshold)
                return op(value, thr)
            except Exception:
                return False
        return False


class RulesEngine:
    def __init__(self, rules_path_pattern='config/rules/*.yaml'):
        self.rules: List[Rule] = []
        self.state = {}  # state to track durations: {rule_id: {'start_ts': float}}
        self.load_rules(rules_path_pattern)

    def load_rules(self, pattern: str):
        self.rules = []
        for path in glob(pattern):
            with open(path, 'r') as fh:
                cfgs = yaml.safe_load(fh)
                if not cfgs:
                    continue
                for r in cfgs:
                    self.rules.append(Rule(r))

    def evaluate_snapshot(self, metrics: Dict[str, float], ts: float = None) -> List[Dict[str, Any]]:
        """Evaluate current metrics and return list of enforcement actions triggered.

        metrics: mapping metric_name -> numeric value
        ts: unix timestamp
        """
        ts = ts or time.time()
        actions = []
        for rule in self.rules:
            trig = rule.trigger
            if 'metric' in trig:
                mname = trig['metric']
                if mname in metrics:
                    val = metrics[mname]
                    matched = rule.match_metric(mname, val)
                    if matched:
                        # handle duration
                        if rule.duration and rule.duration > 0:
                            st = self.state.get(rule.id, {}).get('start_ts')
                            if st is None:
                                # start duration timer
                                self.state.setdefault(rule.id, {})['start_ts'] = ts
                                # not yet triggered
                                continue
                            else:
                                if ts - st >= rule.duration:
                                    actions.append({'rule_id': rule.id, 'actions': rule.enforcement_action})
                                else:
                                    # still waiting for duration
                                    continue
                        else:
                            actions.append({'rule_id': rule.id, 'actions': rule.enforcement_action})
                    else:
                        # reset state if previously started
                        if rule.id in self.state and 'start_ts' in self.state[rule.id]:
                            del self.state[rule.id]['start_ts']
        return actions


if __name__ == '__main__':
    # Simple CLI demo
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--metrics', nargs='*', help='metrics as name=value', default=[])
    args = parser.parse_args()
    metrics = {}
    for m in args.metrics:
        if '=' in m:
            k, v = m.split('=', 1)
            metrics[k] = float(v)
    engine = RulesEngine()
    acts = engine.evaluate_snapshot(metrics)
    if acts:
        print('Enforcement actions:', acts)
    else:
        print('No actions')
