import logging
import typing

import pydantic
import redis.asyncio as redis
from redis.asyncio import client

from infrastructure.brokers import messages_broker

logger = logging.getLogger(__name__)


class RedisMessageBroker(messages_broker.MessageBroker):
    def __init__(
        self,
        redis_factory: typing.Callable[[], redis.Redis],
        timeout_ms: pydantic.PositiveInt = 500,
    ):
        self.connect = redis_factory()

        self.pubsub: client.PubSub | None = None
        self.timeout = float(timeout_ms) / 1000
        self.subscribed_channels = set()

    async def start(self) -> None:
        self.pubsub = self.connect.pubsub()

    async def send_message(self, channel_name: str, message: bytes) -> None:
        logger.debug(f"Sending new message {message} to {channel_name}")
        await self.connect.publish(channel_name, message)

    async def get_message(self) -> bytes | None:
        if self.pubsub is None or not self.pubsub.subscribed:
            raise Exception("Not subscribed")

        message = await self.pubsub.get_message(
            ignore_subscribe_messages=True,
            timeout=self.timeout,
        )

        if message is None:
            return

        if message["type"] != "message":
            return

        return message.get("data")

    async def subscribe(self, channel_name: str) -> None:
        if self.pubsub is None:
            raise Exception("Broker not started")

        logger.debug(f"Subscribing to {channel_name}")
        await self.pubsub.subscribe(channel_name)
        self.subscribed_channels.add(channel_name)

    async def unsubscribe(self, channel_name: str) -> None:
        if self.pubsub is None or not self.pubsub.subscribed:
            raise Exception("Broker not started")

        logger.debug(f"Unsubscribing from {channel_name}")
        await self.pubsub.unsubscribe(channel_name)
        self.subscribed_channels.remove(channel_name)

    async def stop(self) -> None:
        if self.pubsub is None or not self.pubsub.subscribed:
            raise Exception("Broker not started")

        while self.subscribed_channels:
            channel_name = self.subscribed_channels.pop()
            await self.pubsub.unsubscribe(channel_name)
        await self.pubsub.aclose()
