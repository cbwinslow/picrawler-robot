import subprocess
import requests
import time
import os


def test_metrics_endpoint(tmp_path):
    # start the exporter on an ephemeral port
    port = 9100
    env = os.environ.copy()
    env['METRICS_PORT'] = str(port)
    p = subprocess.Popen(["python3", "scripts/metrics_exporter.py", "--port", str(port)], env=env)
    try:
        # wait for exporter to start
        time.sleep(2)
        r = requests.get(f"http://127.0.0.1:{port}/metrics", timeout=5)
        assert r.status_code == 200
        text = r.text
        assert "picrawler_process_cpu_percent" in text
        assert "picrawler_last_heartbeat_timestamp" in text
    finally:
        p.terminate()
        p.wait(timeout=5)
