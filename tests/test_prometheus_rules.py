import yaml


def test_prometheus_alerts_yaml_loads():
    with open('prometheus/rules/picrawler_alerts.yml', 'r') as fh:
        cfg = yaml.safe_load(fh)
    assert 'groups' in cfg
    # basic sanity checks
    names = [g.get('name') for g in cfg['groups']]
    assert 'picrawler-critical' in names
    # ensure at least one rule has an alert field
    found = False
    for g in cfg['groups']:
        for r in g.get('rules', []):
            if 'alert' in r:
                found = True
    assert found
