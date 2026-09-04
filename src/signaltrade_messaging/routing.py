from signaltrade_messaging.config import settings
from signaltrade_messaging.publisher import PermanentPublishError
from signaltrade_messaging.sqs import SqsQueueAdapter

TRADING_MESSAGE_TYPES = frozenset({
    "StrategySignalCreated",
    "PositionReconciled",
    "ManualLiquidationRequested",
})


class UnsupportedMessageType(PermanentPublishError):
    pass


class RoutedQueuePublisher:
    def __init__(self) -> None:
        self.trading = SqsQueueAdapter.from_settings(settings.sqs_trading_command_queue_name)
        self.strategy = SqsQueueAdapter.from_settings(settings.sqs_strategy_command_queue_name)
        self.notification = SqsQueueAdapter.from_settings(settings.sqs_notification_queue_name)

    def publish(self, envelope, *, delay_seconds: int = 0) -> str:
        if envelope.message_type == "AllocationChanged":
            queue = self.strategy
        elif envelope.message_type == "NotificationRequested":
            queue = self.notification
        elif envelope.message_type in TRADING_MESSAGE_TYPES:
            queue = self.trading
        else:
            raise UnsupportedMessageType(
                f"지원하지 않는 메시지 유형입니다: {envelope.message_type}"
            )
        return queue.publish(envelope, delay_seconds=delay_seconds)
