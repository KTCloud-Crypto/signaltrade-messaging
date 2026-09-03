from types import SimpleNamespace

from signaltrade_messaging.routing import RoutedQueuePublisher


def test_routes_contracts_to_owned_queues():
    publisher = object.__new__(RoutedQueuePublisher)
    calls = []
    def queue(name):
        return type("Queue", (), {"publish": lambda self, env, delay_seconds=0: calls.append(name) or name})()
    publisher.strategy, publisher.notification, publisher.trading = queue("strategy"), queue("notification"), queue("trading")
    assert publisher.publish(SimpleNamespace(message_type="AllocationChanged")) == "strategy"
    assert publisher.publish(SimpleNamespace(message_type="NotificationRequested")) == "notification"
    assert publisher.publish(SimpleNamespace(message_type="PositionReconciled")) == "trading"
    assert calls == ["strategy", "notification", "trading"]
