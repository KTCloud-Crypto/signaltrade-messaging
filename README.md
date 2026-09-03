# SignalTrade Messaging

서비스 DB의 Outbox 이벤트를 Queue로 발행하는 Worker입니다.

```text
src/signaltrade_messaging/  Outbox 조회·Queue 발행
tests/                       발행과 재시도 테스트
```

비즈니스 데이터를 소유하지 않습니다. Strategy·Trading·Portfolio 등의 pending Outbox를 읽어 Trading, Portfolio, Notification Queue로 전달합니다.
