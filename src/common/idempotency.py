def process_once(cache: set, msg_id: str):
    """Return 'processed' the first time, 'duplicate' thereafter."""
    if msg_id in cache:
        return "duplicate"
    cache.add(msg_id)
    return "processed"
