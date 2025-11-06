# live-coding/03_inmemory_bus.py
# A tiny in-memory event bus to demo publish/subscribe, retries, idempotency
import time, random

class InMemoryBus:
    def __init__(self):
        self.subs = {}

    def subscribe(self, topic, fn):
        self.subs.setdefault(topic, []).append(fn)

    def publish(self, topic, message):
        for fn in self.subs.get(topic, []):
            fn(message)

# Idempotency helper (dedup by id)
class Deduper:
    def __init__(self):
        self.seen = set()
    def once(self, msg_id):
        if msg_id in self.seen:
            return False
        self.seen.add(msg_id)
        return True

bus = InMemoryBus()
dedup = Deduper()

def email_consumer(evt):
    # Idempotent processing
    if not dedup.once(evt["id"]):
        print(f"[email] duplicate {evt['id']} → drop")
        return
    # Simulate transient failure for some ids
    if evt["id"] % 5 == 0 and evt.get("retry", 0) < 2:
        raise RuntimeError("transient email error")
    print(f"[email] sent to user={evt['user']} for order={evt['id']}")

def safe_wrapper(fn, evt, max_retries=3):
    retry = evt.get("retry", 0)
    try:
        fn(evt)
    except Exception as e:
        retry += 1
        if retry > max_retries:
            print(f"[DLQ] {evt['id']} reason={e}")
        else:
            evt2 = dict(evt); evt2["retry"] = retry
            print(f"[retry] {evt['id']} -> {retry}")
            safe_wrapper(fn, evt2, max_retries)

bus.subscribe("orders", lambda evt: safe_wrapper(email_consumer, evt))

def demo():
    for i in range(1, 12):
        bus.publish("orders", {"id": i, "user": f"user-{i%3}"})
    # Duplicate to show idempotency
    bus.publish("orders", {"id": 2, "user": "user-2"})

if __name__ == "__main__":
    demo()
