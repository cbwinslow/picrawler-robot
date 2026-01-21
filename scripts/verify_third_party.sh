#!/usr/bin/env bash
set -euo pipefail

LOCK=third_party/THIRD_PARTY_LOCK.json
if [ ! -f "$LOCK" ]; then
  echo "No lock file found at $LOCK" >&2
  exit 2
fi

python3 - <<'PY'
import json,subprocess,sys
lock=json.load(open('third_party/THIRD_PARTY_LOCK.json'))
ok=True
for name,meta in lock.items():
    path='third_party/'+name
    try:
        sha=subprocess.check_output(['git','-C',path,'rev-parse','HEAD']).decode().strip()
    except Exception as e:
        print(f'MISSING: {name} at {path} (error: {e})')
        ok=False
        continue
    if sha!=meta['commit']:
        print(f'MISMATCH: {name} expected {meta["commit"]} got {sha}')
        ok=False
    else:
        print(f'OK: {name} at {sha}')
if not ok:
    sys.exit(3)
print('All third_party modules match lock file')
PY
