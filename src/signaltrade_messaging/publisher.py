from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol

from signaltrade_messaging.model import MessageOutbox


class QueuePublisher(Protocol):
    def publish(self, envelope, *, delay_seconds: int = 0) -> str: ...


@dataclass(frozen=True)
class PublishResult:
    selected: int
    published: int
    failed: int


class OutboxPublisher:
    def __init__(self, queue: QueuePublisher, max_retry_seconds: int = 300) -> None:
        self.queue, self.max_retry_seconds = queue, max_retry_seconds

    def publish_pending(self, db, limit: int = 100,
                        now: datetime | None = None) -> PublishResult:
        if limit <= 0:
            raise ValueError("limit must be greater than zero")
        current = now or datetime.now(timezone.utc)
        pending = (db.query(MessageOutbox).filter(
            MessageOutbox.status == "pending", MessageOutbox.next_attempt_at <= current)
            .order_by(MessageOutbox.created_at, MessageOutbox.id)
            .with_for_update(skip_locked=True).limit(limit).all())
        published = failed = 0
        for message in pending:
            message.attempt_count += 1
            try:
                transport_id = self.queue.publish(message.to_envelope())
            except Exception as error:
                failed += 1
                message.next_attempt_at = current + timedelta(
                    seconds=min(2 ** min(message.attempt_count, 8), self.max_retry_seconds))
                message.last_error = str(error)[:2000]
            else:
                published += 1
                message.status = "published"
                message.transport_message_id = transport_id
                message.published_at = current
                message.last_error = None
        db.flush()
        return PublishResult(len(pending), published, failed)
