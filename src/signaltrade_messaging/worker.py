import logging
import signal
import threading

from prometheus_client import Counter, start_http_server

from signaltrade_messaging.config import settings
from signaltrade_messaging.database import SessionLocal
from signaltrade_messaging.publisher import OutboxPublisher
from signaltrade_messaging.routing import RoutedQueuePublisher

logger = logging.getLogger(__name__)
PUBLISHED = Counter("signaltrade_outbox_published_total", "Published outbox messages")
FAILED = Counter("signaltrade_outbox_failed_total", "Failed outbox messages")


def publish_once(publisher: OutboxPublisher) -> tuple[int, int, int]:
    with SessionLocal() as db:
        result = publisher.publish_pending(db)
        db.commit()
    PUBLISHED.inc(result.published)
    FAILED.inc(result.failed)
    return result.selected, result.published, result.failed


def run() -> None:
    logging.basicConfig(level=settings.log_level.upper())
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    if settings.metrics_enabled:
        start_http_server(settings.messaging_metrics_port)
    publisher = OutboxPublisher(RoutedQueuePublisher())
    logger.info("Outbox publisher started")
    while not stop.is_set():
        try:
            selected, published, failed = publish_once(publisher)
            if selected:
                logger.info("Outbox cycle: selected=%s published=%s failed=%s",
                            selected, published, failed)
        except Exception:
            logger.exception("Outbox publish cycle failed; retrying")
        stop.wait(max(.1, settings.outbox_poll_seconds))
