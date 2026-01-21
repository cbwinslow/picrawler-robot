import importlib
import types


def test_stop_motors_uses_robot_hat(monkeypatch):
    # Create a fake robot_hat with Motors.stop
    fake_motors = types.SimpleNamespace(stop=lambda: setattr(fake_motors, 'stopped', True))
    fake_robot_hat = types.SimpleNamespace(Motors=lambda: fake_motors)

    monkeypatch.setitem(__import__('sys').modules, 'robot_hat', fake_robot_hat)

    from scripts.enforcement import stop_motors
    ok = stop_motors(dry_run=False)
    assert ok
    assert getattr(fake_motors, 'stopped', False) is True
