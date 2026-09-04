from types import SimpleNamespace

import pytest

from signaltrade_messaging.routing import RoutedQueuePublisher, UnsupportedMessageType


def test_routes_contracts_to_owned_queues():
    publisher = object.__new__(RoutedQueuePublisher)
    calls = []
    def queue(name):
        return type("Queue", (), {"publish": lambda self, env, delay_seconds=0: calls.append(name) or name})()
    publisher.strategy, publisher.notification, publisher.trading = queue("strategy"), queue("notification"), queue("trading")
    assert publisher.publish(SimpleNamespace(message_type="AllocationChanged")) == "strategy"
    assert publisher.publish(SimpleNamespace(message_type="NotificationRequested")) == "notification"
    assert publisher.publish(SimpleNamespace(message_type="PositionReconciled")) == "trading"
    assert publisher.publish(SimpleNamespace(message_type="StrategySignalCreated")) == "trading"
    assert publisher.publish(SimpleNamespace(message_type="ManualLiquidationRequested")) == "trading"
    assert calls == ["strategy", "notification", "trading", "trading", "trading"]


def test_rejects_unknown_message_type_instead_of_routing_it_to_trading():
    publisher = object.__new__(RoutedQueuePublisher)
    calls = []
    publisher.strategy = publisher.notification = publisher.trading = type(
        "Queue", (), {"publish": lambda self, env, delay_seconds=0: calls.append(env)})()

    with pytest.raises(UnsupportedMessageType, match="TypoSignalCreated"):
        publisher.publish(SimpleNamespace(message_type="TypoSignalCreated"))

    assert calls == []
