import yaml


def test_ai_agent_config_has_required_fields():
    with open('config/agents/ai.yaml', 'r') as fh:
        cfg = yaml.safe_load(fh)
    required = {'id', 'name', 'run_mode', 'model'}
    assert required.issubset(set(cfg.keys())), 'AI agent config missing required fields'