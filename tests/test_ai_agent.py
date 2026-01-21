import os
import importlib


def test_ai_agent_fallback(monkeypatch):
    # Ensure no API key set -> fallback used
    monkeypatch.delenv('OPENROUTER_API_KEY', raising=False)
    ai = importlib.import_module('scripts.ai_agent')
    out = ai.respond('hello')
    assert out.startswith('(local)')


def test_ai_agent_uses_openrouter(monkeypatch):
    # Mock openrouter module
    class FakeClient:
        def __init__(self, api_key=None):
            pass
        def complete(self, prompt=None):
            return {'text': 'fake reply'}
    fake_openrouter = type('M', (), {'OpenRouter': FakeClient})
    monkeypatch.setitem(__import__('sys').modules, 'openrouter', fake_openrouter)
    monkeypatch.setenv('OPENROUTER_API_KEY', 'FAKE')
    ai = importlib.import_module('scripts.ai_agent')
    out = ai.respond('hello')
    assert 'fake reply' in out
