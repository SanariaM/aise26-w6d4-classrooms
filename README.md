# W6D4 – Event-Driven Architecture (RabbitMQ + Kafka/Redpanda)

This repo contains the **required code** for the W6D4 session: minimal, working examples for
RabbitMQ and Kafka (or Redpanda) plus a fallback in‑memory bus and a small idempotency test.

## Quick Start

### 0) Python env & deps
```bash
python3 -m venv .venv
source .venv/bin/activate           # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 1) Run RabbitMQ (Docker)
```bash
docker run -it --rm -p 5672:5672 -p 15672:15672 rabbitmq:3-management
# UI: http://localhost:15672  (guest / guest)
```

### 2) Run Redpanda (Kafka API compatible) – easiest single-binary Kafka
```bash
docker run -it --rm -p 9092:9092 -p 9644:9644   docker.redpanda.com/redpandadata/redpanda:latest   redpanda start --overprovisioned --smp 1 --memory 1G --reserve-memory 0M   --node-id 0 --check=false --kafka-addr 0.0.0.0:9092
```

> **No Docker?** Use `live-coding/03_inmemory_bus.py` to demo producer/consumer logic without brokers.

---

## Live Coding A — RabbitMQ (ack + prefetch + retry + DLQ)

**Producer (Terminal A):**
```bash
python live-coding/01_rabbitmq_queue.py produce
```

**Consumer (Terminal B):**
```bash
python live-coding/01_rabbitmq_queue.py
```

Change knobs:
- `prefetch` → back‑pressure
- `max_retries` → bounded retries; on exceed → **DLQ**

Inspect queues in RabbitMQ UI → Queues → `w6d4.tasks` and `w6d4.tasks.dlq`.

---

## Live Coding B — Kafka/Redpanda (topics, partitions, consumer groups, ordering)

**Producer:**
```bash
python live-coding/02_kafka_partitions.py produce
```

**Consumers (same consumer group):**
```bash
python live-coding/02_kafka_partitions.py C1
python live-coding/02_kafka_partitions.py C2
```

Observe:
- Same key → same partition → **per‑key ordering**
- Consumers in the same group split partitions → **parallelism**
- Try adding a third consumer and watch **rebalancing**

---

## Fallback — In‑Memory Bus

If brokers aren't available, run:
```bash
python live-coding/03_inmemory_bus.py
```
This simulates publish/subscribe, idempotency, and retry semantics in one file.

---

## Tests — Idempotency

```bash
pytest -q
```

The unit test ensures a simple dedup cache only processes each message once.

---

## Repo Layout

```
W6D4-eda/
├─ requirements.txt
├─ README.md
├─ lesson-materials/
│  ├─ pubsub-vs-queue.png            # (placeholder)
│  └─ consumer-group.png             # (placeholder)
├─ live-coding/
│  ├─ 01_rabbitmq_queue.py           # RabbitMQ demo (prefetch, retry, DLQ)
│  ├─ 02_kafka_partitions.py         # Kafka demo (partitions, groups, ordering)
│  └─ 03_inmemory_bus.py             # Brokerless fallback
├─ src/
│  ├─ notifications/                 # (empty: starter spot for assignment)
│  ├─ analytics/                     # (empty: starter spot for assignment)
│  └─ common/
│     └─ idempotency.py              # helper + exported in tests
├─ tests/
│  └─ test_idempotency.py
└─ docker/                           # (room for compose if you add one)
```

---

## Notes
- Scripts are intentionally minimal and verbose for teaching.
- Safe to extend for homework (DLQ policies, idempotency, hot‑partition mitigation).
