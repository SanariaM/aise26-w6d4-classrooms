Repo layout (typical)
.
├─ src/
│  ├─ common/
│  │  └─ idempotency.py
│  ├─ notifications/           # RabbitMQ path
│  │  ├─ producer.py
│  │  ├─ consumer.py
│  │  └─ config.py
│  └─ analytics/               # Kafka path
│     ├─ producer.py
│     ├─ consumer.py
│     └─ config.py
├─ scripts/
│  ├─ load_test.py
│  └─ demo_run.sh
├─ tests/
│  ├─ test_idempotency.py
│  └─ test_load_min.py
├─ docker/
│  ├─ rabbitmq.sh      # optional helper
│  └─ redpanda.sh      # optional helper
├─ .github/workflows/ci.yml
├─ README.md
└─ ARCHITECTURE.png (or .drawio/.pdf)
