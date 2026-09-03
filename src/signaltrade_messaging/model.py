from datetime import timezone

from sqlalchemy import Column, DateTime, Index, Integer, JSON, String, Text, func

from signaltrade_messaging.database import Base
from signaltrade_messaging.envelope import MessageEnvelope


class MessageOutbox(Base):
    __tablename__ = "message_outbox"
    __table_args__ = (Index("ix_message_outbox_pending", "status", "next_attempt_at", "created_at"),)
    id = Column(Integer, primary_key=True)
    message_id = Column(String(36), nullable=False, unique=True)
    message_type = Column(String(128), nullable=False, index=True)
    correlation_id = Column(String(128), nullable=False, index=True)
    producer = Column(String(64), nullable=False)
    schema_version = Column(Integer, nullable=False, default=1)
    idempotency_key = Column(String(255), unique=True)
    payload = Column(JSON, nullable=False, default=dict)
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(16), nullable=False, default="pending")
    attempt_count = Column(Integer, nullable=False, default=0)
    next_attempt_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_error = Column(Text)
    transport_message_id = Column(String(128))
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    def to_envelope(self) -> MessageEnvelope:
        occurred_at = self.occurred_at
        if occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
            occurred_at = occurred_at.replace(tzinfo=timezone.utc)
        return MessageEnvelope(message_id=self.message_id, message_type=self.message_type,
            occurred_at=occurred_at, correlation_id=self.correlation_id,
            producer=self.producer, schema_version=self.schema_version,
            idempotency_key=self.idempotency_key, payload=self.payload)
