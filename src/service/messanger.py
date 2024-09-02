import contextlib
import typing
import uuid

import orjson

from domain import message as message_entity
from infrastructure.brokers import protocol as broker_protocol
from infrastructure.database.persistent import protocol as repository_protocol
from service import exceptions


class Messanger:
    """
    Messanger service.
    """

    def __init__(
        self,
        broker: broker_protocol.MessageBroker,
        uow: repository_protocol.MessageUoW,
    ) -> None:
        self.broker = broker
        self.uow = uow
        self._subscription_started = False

    @contextlib.asynccontextmanager
    async def start_subscription(self, target_account: typing.Text):
        """
        Opens subscription to broker for the specified account.
        """
        try:
            await self.broker.start()
            await self.broker.subscribe(target_account)
            self._subscription_started = True
            yield
        except Exception as e:
            raise exceptions.StartSubscriptionError(target_account, e)
        finally:
            await self.broker.stop()
            self._subscription_started = False

    async def send_message(self, message: message_entity.Message) -> None:
        """
        Sends message to broker
        """
        async with self.uow as repository:
            await self.broker.send_message(
                message.receiver,
                orjson.dumps(message.model_dump(mode="json")),
            )
            await repository.add(message)
            await repository.commit()

    async def wait_message(self) -> message_entity.Message | None:
        """
        Returns new messages from broker in real-time mode for the specified account.
        """
        if not self._subscription_started:
            raise Exception(
                "Not subscribed. Open context manager to start subscription.",
            )

        message_bytes = await self.broker.get_message()
        if message_bytes is None:
            return None

        message = message_entity.Message.model_validate(orjson.loads(message_bytes))

        async with self.uow as repository:
            await repository.change_status(
                message.message_id,
                message_entity.MessageStatus.DELIVERED,
            )
            await repository.commit()

        return message

    async def mark_as_received(
        self,
        receiver: typing.Text,
        message_id: uuid.UUID,
    ) -> None:
        """
        Marks message as received
        """
        async with self.uow as repository:
            message = await repository.get(message_id)

            if message is None:
                raise exceptions.MessageNotFound(message_id)

            if message.receiver != receiver:
                raise exceptions.ChangeStatusAccessDonated(
                    receiver,
                    message_id,
                    message_entity.MessageStatus.RECEIVED,
                )

            await repository.change_status(
                message_id,
                message_entity.MessageStatus.RECEIVED,
            )
            await repository.commit()

    async def mark_as_read(self, reader: typing.Text, message_id: uuid.UUID) -> None:
        """
        Marks message as read
        """
        async with self.uow as repository:
            message = await repository.get(message_id)

            if message is None:
                raise exceptions.MessageNotFound(message_id)

            if message.receiver != reader:
                raise exceptions.ChangeStatusAccessDonated(
                    reader,
                    message_id,
                    message_entity.MessageStatus.READ,
                )

            await repository.change_status(
                message_id,
                message_entity.MessageStatus.READ,
            )
            await repository.commit()

    async def delete_message(self, deleter: typing.Text, message_id: uuid.UUID) -> None:
        """
        Marks message as deleted
        """
        async with self.uow as repository:
            message = await repository.get(message_id)

            if message is None:
                raise exceptions.MessageNotFound(message_id)

            if deleter not in (message.receiver, message.sender):
                raise exceptions.ChangeStatusAccessDonated(
                    deleter,
                    message_id,
                    message_entity.MessageStatus.DELETED,
                )

            await repository.change_status(
                message_id,
                message_entity.MessageStatus.DELETED,
            )
            await repository.commit()
