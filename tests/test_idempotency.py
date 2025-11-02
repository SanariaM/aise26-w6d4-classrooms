# very small sanity test for a dedup cache
def process_once(cache: set, msg_id: str):
    if msg_id in cache:
        return "duplicate"
    cache.add(msg_id)
    return "processed"

def test_idempotency_cache():
    seen = set()
    assert process_once(seen, "A") == "processed"
    assert process_once(seen, "A") == "duplicate"
    assert process_once(seen, "B") == "processed"