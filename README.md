# SignalTrade Messaging

서비스별 DB 변경과 SQS 메시지 발행 사이를 연결하는 **Outbox Publisher**입니다. 각 도메인 서비스가 `message_outbox`에 남긴 이벤트를 읽고, 이벤트 종류에 맞는 Queue로 전달합니다.

## Outbox가 필요한 이유

DB 저장과 Queue 발행을 별도로 실행하면 둘 중 하나만 성공할 수 있습니다. 예를 들어 주문 신호는 DB에 저장됐지만 Queue 전송 중 장애가 나면 주문 Worker가 신호를 받지 못합니다.

이를 줄이기 위해 도메인 서비스는 업무 데이터와 Outbox 이벤트를 하나의 DB transaction으로 저장합니다. Messaging은 아직 발행되지 않은 이벤트를 반복해서 조회하고 성공할 때까지 재시도합니다.

```text
업무 데이터 + Outbox 저장 → Messaging 조회 → SQS 발행 → 발행 완료 표시
```

## 주요 역할

- 발행 대기 중인 Outbox 행 조회와 잠금
- 메시지 타입에 따른 Queue 선택
- SQS 메시지 발행과 발행 완료 상태 기록
- 실패 횟수와 마지막 오류 기록 및 재시도
- 여러 Publisher가 실행될 때 같은 행을 동시에 처리하지 않도록 제어
- Queue 발행 지연과 실패 상태를 로그와 지표로 노출

## 데이터 권한

자체 도메인 테이블은 소유하지 않습니다. 공유 `message_outbox`에서 다음과 같은 **발행 관리 필드만** 변경합니다.

- 발행 상태와 발행 완료 시각
- 재시도 횟수와 다음 시도 시각
- 마지막 오류와 처리 잠금 정보

Outbox에 담긴 업무 내용이나 각 서비스의 도메인 테이블은 수정하지 않습니다.

## Queue 전달 규칙

- Trading Queue
  - `StrategySignalCreated`
  - `PositionReconciled`
  - `ManualLiquidationRequested`
- Strategy Queue
  - `AllocationChanged`
- Notification Queue
  - `NotificationRequested`

로컬은 LocalStack SQS, 운영은 AWS SQS를 사용합니다. 연결 방식만 환경 변수로 바뀌며 이벤트 계약과 routing 규칙은 동일합니다. Messaging 자체는 Redis를 사용하지 않습니다.
