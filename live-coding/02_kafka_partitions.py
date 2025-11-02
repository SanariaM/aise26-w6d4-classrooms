import os, time, json, threading, random
from kafka import KafkaProducer, KafkaConsumer, TopicPartition
BOOT = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = "w6d4.events"

def mk_producer():
    return KafkaProducer(bootstrap_servers=BOOT,
        value_serializer=lambda v: json.dumps(v).encode())

def mk_consumer(group_id: str):
    return KafkaConsumer(TOPIC,
        bootstrap_servers=BOOT,
        group_id=group_id,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda b: json.loads(b.decode()))

def produce(n=50):
    p = mk_producer()
    for i in range(n):
        key = f"user-{i%7}" # same user routes to same partition (ordering)
        evt = {"i": i, "user": key, "ts": time.time()}
        p.send(TOPIC, value=evt)
        print("→", evt)
        time.sleep(0.03)
    p.flush()

def consume(name: str, group="w6d4-group"):
    c = mk_consumer(group)
    for msg in c:
        v = msg.value
        print(f"{name} got i={v['i']} user={v['user']} part={msg.partition} off={msg.offset}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "produce":
        produce(80)
    else:
        who = sys.argv[1] if len(sys.argv) > 1 else "C1"
        consume(who)