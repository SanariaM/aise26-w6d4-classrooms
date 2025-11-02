import json, os, time, random
import pika
RABBIT_URL = os.getenv("RABBIT_URL", "amqp://guest:guest@localhost:5672/%2F")
QUEUE = "w6d4.tasks"
DLQ = "w6d4.tasks.dlq"
EXCHANGE = "" # default direct exchange
def mk_conn():
    params = pika.URLParameters(RABBIT_URL)
    return pika.BlockingConnection(params)

def setup():
    conn = mk_conn()
    ch = conn.channel()

    # DLQ: bind DLQ queue
    ch.queue_declare(queue=DLQ, durable=True)
    # Main queue with DLX (dead-letter-exchange) routing to DLQ
    ch.queue_declare(queue=QUEUE, durable=True, arguments={
        "x-dead-letter-exchange": EXCHANGE,
        "x-dead-letter-routing-key": DLQ
    })
    conn.close()

def produce(n=10):
    conn = mk_conn()
    ch = conn.channel()
    for i in range(n):
        body = json.dumps({"id": i, "work_ms": random.randint(50, 300)})
        ch.basic_publish(EXCHANGE, QUEUE, body.encode(),
            pika.BasicProperties(delivery_mode=2)) # persistent
        print("→ sent", body)
    conn.close()

def consume(prefetch=5, max_retries=3):
    conn = mk_conn()
    ch = conn.channel()
    ch.basic_qos(prefetch_count=prefetch) # back-pressure
    RETRY_HDR = "x-retry-count"

    def handle(ch_, method, props, body):
        msg = json.loads(body.decode())
        retry = int(props.headers.get(RETRY_HDR, 0)) if props and props.headers else 0

        try:
            # Simulate occasional failure
            if msg["id"] % 7 == 0 and retry < 2:
                raise RuntimeError("transient error")
            time.sleep(msg["work_ms"]/1000.0) # "work"
            print(f"✓ processed id={msg['id']} in {msg['work_ms']}ms")
            ch_.basic_ack(method.delivery_tag)
        except Exception as e:
            retry += 1
            if retry > max_retries:
                print(f"✗ DLQ id={msg['id']} after {retry-1} retries")
                ch_.basic_nack(method.delivery_tag, requeue=False) # send to DLQ
            else:
                # requeue with retry header incremented
                print(f"... retry id={msg['id']} count={retry}")
                ch_.basic_publish(EXCHANGE, QUEUE, body,
                    pika.BasicProperties(headers={RETRY_HDR: retry}, delivery_mode=2))
                ch_.basic_ack(method.delivery_tag)

    ch.basic_consume(queue=QUEUE, on_message_callback=handle, auto_ack=False)
    print(" [*] Consuming. Ctrl+C to stop.")

    try:
        ch.start_consuming()
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    setup()
    if len(sys.argv) > 1 and sys.argv[1] == "produce":
        produce(15)
    else:
        consume(prefetch=5, max_retries=3)