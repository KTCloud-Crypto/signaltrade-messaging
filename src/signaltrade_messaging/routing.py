from signaltrade_messaging.config import settings
from signaltrade_messaging.sqs import SqsQueueAdapter


class RoutedQueuePublisher:
    def __init__(self) -> None:
        self.trading = SqsQueueAdapter.from_settings(settings.sqs_trading_command_queue_name)
        self.strategy = SqsQueueAdapter.from_settings(settings.sqs_strategy_command_queue_name)
        self.notification = SqsQueueAdapter.from_settings(settings.sqs_notification_queue_name)

    def publish(self, envelope, *, delay_seconds: int = 0) -> str:
        queue = (self.strategy if envelope.message_type == "AllocationChanged" else
                 self.notification if envelope.message_type == "NotificationRequested" else
                 self.trading)
        return queue.publish(envelope, delay_seconds=delay_seconds)
