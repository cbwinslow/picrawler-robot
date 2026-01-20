import time
from scripts.rules_engine import RulesEngine


def test_battery_low_triggers_stop():
    engine = RulesEngine()

    # Simulate no previous state: feed voltages above threshold -> nothing
    t0 = time.time()
    acts = engine.evaluate_snapshot({'picrawler_battery_voltage_volts': 6.5}, ts=t0)
    assert acts == []

    # simulate voltage falling below 6.0 -> start timer
    acts = engine.evaluate_snapshot({'picrawler_battery_voltage_volts': 5.9}, ts=t0 + 1)
    assert acts == []  # duration not completed (15s)

    # after duration (simulate 16 seconds later)
    acts = engine.evaluate_snapshot({'picrawler_battery_voltage_volts': 5.8}, ts=t0 + 16)
    assert any(a['rule_id'] == 'safety/battery-low' for a in acts)


def test_overtemp_triggers_throttle():
    engine = RulesEngine()
    t0 = time.time()
    acts = engine.evaluate_snapshot({'picrawler_cpu_temp_celsius': 86}, ts=t0)
    # overtemp rule has duration 10s in config; first sample should start timer
    assert acts == []
    acts = engine.evaluate_snapshot({'picrawler_cpu_temp_celsius': 90}, ts=t0 + 12)
    assert any(a['rule_id'] == 'safety/overtemp' for a in acts)
