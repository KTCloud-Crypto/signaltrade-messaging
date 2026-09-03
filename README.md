# signaltrade-messaging

공유 PostgreSQL의 pending Outbox를 잠금 조회해 메시지 계약에 맞는 SQS queue로 전달하는
독립 Publisher입니다. 비즈니스 데이터나 서비스별 모델은 소유하지 않습니다.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/pytest
```

기준: `KTCloud-Crypto` `feat/132`의 `013107a`.
