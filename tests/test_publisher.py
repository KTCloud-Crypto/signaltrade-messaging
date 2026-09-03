from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from signaltrade_messaging.model import MessageOutbox
from signaltrade_messaging.publisher import OutboxPublisher


def session_with_message():
    engine = create_engine("sqlite://")
    MessageOutbox.__table__.create(engine)
    db = sessionmaker(bind=engine)()
    message = MessageOutbox(message_id=str(uuid4()), message_type="StrategySignalCreated",
        correlation_id="c", producer="strategy", schema_version=1, payload={"id": 1},
        occurred_at=datetime.now(timezone.utc), next_attempt_at=datetime.now(timezone.utc))
    db.add(message); db.flush()
    return db, message


def test_success_marks_published():
    db, message = session_with_message()
    queue = type("Queue", (), {"publish": lambda self, envelope, delay_seconds=0: "sqs-1"})()
    result = OutboxPublisher(queue).publish_pending(db, now=datetime.now(timezone.utc) + timedelta(seconds=1))
    assert (result.selected, result.published, result.failed) == (1, 1, 0)
    assert message.status == "published" and message.transport_message_id == "sqs-1"


def test_failure_delays_retry():
    db, message = session_with_message()
    def fail(*args, **kwargs): raise RuntimeError("queue unavailable")
    queue = type("Queue", (), {"publish": fail})()
    now = datetime.now(timezone.utc) + timedelta(seconds=1)
    result = OutboxPublisher(queue).publish_pending(db, now=now)
    assert (result.published, result.failed) == (0, 1)
    assert message.status == "pending" and message.next_attempt_at == now + timedelta(seconds=2)
