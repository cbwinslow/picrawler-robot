import os
import tempfile
import requests

from scripts.alerting import send_alert, LAST_ALERT_PATH


class DummyResponse:
    def __init__(self, status_code=200, text='ok'):
        self.status_code = status_code
        self.text = text


def test_send_alert_success(monkeypatch, tmp_path):
    # Monkeypatch requests.post to return success
    def fake_post(url, json, headers, timeout):
        return DummyResponse(200, 'ok')
    monkeypatch.setattr('requests.post', fake_post)

    # ensure the last alert path is writable in test
    monkeypatch.setenv('PICRAWLER_ALERT_RATE_LIMIT', '0')
    ok = send_alert('http://example.com/webhook', {'msg': 'test'}, retries=1)
    assert ok


def test_send_alert_rate_limit(monkeypatch, tmp_path):
    # write a recent timestamp to last alert path to trigger rate limit
    p = tmp_path / 'last'
    p.write_text(str(float( ( __import__('time').time() ) )))
    monkeypatch.setenv('PICRAWLER_ALERT_RATE_LIMIT', '1000')
    monkeypatch.setattr('scripts.alerting.LAST_ALERT_PATH', str(p))
    ok = send_alert('http://example.com/webhook', {'msg': 'test'}, retries=1)
    assert ok is False
