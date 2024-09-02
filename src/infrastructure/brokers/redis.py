import logging
import typing

import pydantic
import redis.asyncio as redis

from infrastructure.brokers import protocol

logger = logging.getLogger(__name__)


class RedisMessageBroker(protocol.MessageBroker):

    def __init__(self, connect: redis.Redis, timeout_ms: pydantic.PositiveInt = 500):
        self.connect = connect
        self.pubsub: redis.client.PubSub | None = None
        self.timeout = float(timeout_ms) / 1000
        self.subscribed_channels = set()

    def start(self) -> None:
        self.pubsub = self.connect.pubsub()

    async def send_message(self, channel_name: typing.Text, message: bytes) -> None:
        logger.debug(f"Sending new message {channel_name}")
        await self.connect.publish(channel_name, message)

    async def get_message(self) -> bytes | None:
        if self.pubsub is None or not self.pubsub.subscribed:
            raise Exception("Not subscribed")

        message = await self.pubsub.get_message(ignore_subscribe_messages=True, timeout=self.timeout)

        if message["type"] != "message":
            return

        return message

    async def subscribe(self, channel_name: typing.Text) -> None:
        logger.debug(f"Subscribing to {channel_name}")
        await self.pubsub.subscribe(channel_name)
        self.subscribed_channels.add(channel_name)

    async def unsubscribe(self, channel_name: typing.Text) -> None:
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
