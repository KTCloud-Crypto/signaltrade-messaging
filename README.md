# SignalTrade Messaging

각 서비스 DB에 안전하게 기록된 Outbox 이벤트를 읽어 SQS Queue로 발행하는 독립 Worker입니다. 메시지 전달 역할만 가지며 전략·주문·사용자 같은 비즈니스 데이터를 소유하지 않습니다.

## 주요 책임

- pending Outbox 행을 잠금 방식으로 조회
- 메시지 타입에 따라 대상 Queue 선택
- 발행 성공·실패·재시도 상태 기록
- 중복 발행을 줄이기 위한 idempotency key 사용
- Queue 발행 지연과 실패를 metric·로그로 노출

## 디렉터리

```text
src/signaltrade_messaging/
  worker.py          polling과 발행 실행
  outbox.py          Outbox 잠금·상태 변경
  queue_publisher.py SQS·LocalStack 발행 처리
  contracts.py       메시지 envelope 처리
tests/               발행·재시도·중복 방지 테스트
```

## 메시지 흐름

```text
Strategy Outbox  → Trading Queue      → Trading Worker
Trading Outbox   → Portfolio Queue    → Portfolio Worker
Trading Outbox   → Notification Queue → Notification Worker
Portfolio Outbox → Notification Queue → Notification Worker
```

로컬에서는 LocalStack SQS를 사용하고, 운영에서는 같은 인터페이스로 AWS SQS를 사용합니다.

## 로컬 확인

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/pytest
```

Worker는 kind의 `outbox-publisher` Deployment로 실행됩니다.
