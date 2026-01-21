import time
from scripts.rules_engine import RulesEngine


def test_battery_low_duration():
    engine = RulesEngine('config/rules/safety_battery-low.yaml')
    t0 = 1_700_000_000.0
    # initial high reading should not trigger
    acts = engine.evaluate_snapshot({'picrawler_battery_voltage_volts': 6.5}, ts=t0)
    assert acts == []
    # low reading starts duration window
    acts = engine.evaluate_snapshot({'picrawler_battery_voltage_volts': 5.5}, ts=t0 + 1)
    assert acts == []  # duration not yet reached; state started
    # after duration completes
    acts = engine.evaluate_snapshot({'picrawler_battery_voltage_volts': 5.0}, ts=t0 + 16)
    assert any(a['rule_id'] == 'safety/battery-low' for a in acts)
    assert any('stop_motors' in a['actions'] for a in acts)


def test_overtemp_triggers_after_duration():
    engine = RulesEngine('config/rules/safety_overtemp.yaml')
    t0 = 1_700_000_100.0
    acts = engine.evaluate_snapshot({'picrawler_cpu_temp_celsius': 86}, ts=t0)
    assert acts == []  # duration 10s begins
    acts = engine.evaluate_snapshot({'picrawler_cpu_temp_celsius': 87}, ts=t0 + 11)
    assert any(a['rule_id'] == 'safety/overtemp' for a in acts)
    assert any('throttle_cpu_tasks' in a['actions'] for a in acts)


def test_collision_immediate():
    engine = RulesEngine('config/rules/safety_collision-imminent.yaml')
    acts = engine.evaluate_snapshot({'ultrasonic_distance_m': 0.05})
    assert any(a['rule_id'] == 'safety/collision-imminent' for a in acts)
    assert any('stop_motors' in a['actions'] for a in acts)


def test_privacy_block_upload():
    engine = RulesEngine('config/rules/privacy_no-raw-frame-upload.yaml')
    acts = engine.evaluate_snapshot({'camera_raw_upload_attempt': 1})
    assert any(a['rule_id'] == 'privacy/no-raw-frame-upload' for a in acts)
    assert any('block_upload' in a['actions'] for a in acts)
