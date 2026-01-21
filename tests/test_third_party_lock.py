import json


def test_third_party_lock_exists():
    with open('third_party/THIRD_PARTY_LOCK.json','r') as fh:
        lock=json.load(fh)
    assert lock
    for name,meta in lock.items():
        assert 'url' in meta and 'commit' in meta
