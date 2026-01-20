import glob
import yaml


required_agent_fields = {"id", "name", "description", "inputs", "outputs", "safety_level"}


def test_agent_configs_have_required_fields():
    files = glob.glob("config/agents/*.yaml")
    assert files, "No agent configs found"
    for f in files:
        with open(f, "r") as fh:
            cfg = yaml.safe_load(fh)
        assert required_agent_fields.issubset(set(cfg.keys())), f"Missing fields in {f}: {required_agent_fields - set(cfg.keys())}"


required_rule_fields = {"id", "severity", "description", "trigger", "enforcement_action"}


def test_rules_have_required_fields():
    files = glob.glob("config/rules/*.yaml")
    assert files, "No rule configs found"
    for f in files:
        with open(f, "r") as fh:
            cfgs = yaml.safe_load(fh)
        # file can contain list of rules
        for rule in cfgs:
            assert required_rule_fields.issubset(set(rule.keys())), f"Missing fields in {f} rule {rule.get('id')}"
