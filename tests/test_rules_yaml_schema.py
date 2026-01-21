import glob
import yaml


REQUIRED_FIELDS = ['id', 'trigger', 'enforcement_action']


def test_rules_have_required_fields():
    files = glob.glob('config/rules/*.yaml')
    assert files, "No rule files found"
    for path in files:
        with open(path, 'r') as fh:
            cfgs = yaml.safe_load(fh) or []
        for r in cfgs:
            for f in REQUIRED_FIELDS:
                assert f in r, f"Missing {f} in {path}"
            assert 'metric' in r['trigger'], f"Missing trigger.metric in {path}"
            assert isinstance(r['enforcement_action'], list), f"enforcement_action must be a list in {path}"
