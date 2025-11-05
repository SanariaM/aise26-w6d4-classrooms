├── src/
│ ├── common/
│ │ └── idempotency.py
│ ├── notifications/
│ │ ├── producer.py
│ │ ├── consumer.py
│ │ └── config.py
│ └── analytics/
│ ├── producer.py
│ ├── consumer.py
│ └── config.py
├── tests/
│ ├── test_idempotency.py
│ └── test_load_min.py
├── scripts/
│ ├── load_test.py
│ └── demo_run.sh
├── docker/
│ ├── rabbitmq.sh
│ └── redpanda.sh
├── .github/workflows/ci.yml
├── ARCHITECTURE.png
└── README.md
