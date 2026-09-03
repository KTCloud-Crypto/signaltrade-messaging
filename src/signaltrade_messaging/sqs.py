from typing import Any

import boto3

from signaltrade_messaging.config import settings
from signaltrade_messaging.envelope import MessageEnvelope


class SqsQueueAdapter:
    def __init__(self, client: Any, queue_name: str) -> None:
        self._client, self._queue_name, self._queue_url = client, queue_name, None

    @classmethod
    def from_settings(cls, queue_name: str) -> "SqsQueueAdapter":
        options: dict[str, Any] = {"region_name": settings.aws_region}
        if settings.sqs_endpoint_url:
            options["endpoint_url"] = settings.sqs_endpoint_url
        return cls(boto3.client("sqs", **options), queue_name)

    def publish(self, envelope: MessageEnvelope, *, delay_seconds: int = 0) -> str:
        if self._queue_url is None:
            self._queue_url = self._client.get_queue_url(QueueName=self._queue_name)["QueueUrl"]
        response = self._client.send_message(
            QueueUrl=self._queue_url, MessageBody=envelope.to_json(), DelaySeconds=delay_seconds,
            MessageAttributes={"message_type": {"DataType": "String", "StringValue": envelope.message_type},
                               "schema_version": {"DataType": "Number", "StringValue": str(envelope.schema_version)}})
        return response["MessageId"]
