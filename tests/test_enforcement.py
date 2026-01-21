from scripts.enforcement import perform_actions


def test_perform_actions_dry_run():
    results = perform_actions(['stop_motors', 'throttle_cpu_tasks', 'alert_operator'], dry_run=True)
    assert all(isinstance(r, tuple) for r in results)
    assert all(r[1] for r in results)


def test_unknown_action_logged():
    results = perform_actions(['nonexistent_action'], dry_run=True)
    assert results == [('nonexistent_action', False)]
