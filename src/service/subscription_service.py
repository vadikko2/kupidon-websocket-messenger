import contextlib
import typing

import cqrs
import orjson

from domain import messages
from infrastructure.brokers import protocol as broker_protocol
from service import exceptions, unit_of_work


class SubscriptionService:
    """
    Subscription service.
    """

    def __init__(
        self,
        broker: broker_protocol.MessageBroker,
        uow: unit_of_work.UoW,
    ) -> None:
        self.broker = broker
        self.uow = uow
        self.subscription_started = False
        self.target_account: typing.Text | None = None

    @contextlib.asynccontextmanager
    async def start_subscription(self, target_account: typing.Text):
        """
        Opens subscription to broker for the specified account.
        """
        try:
            await self.broker.start()
            await self.broker.subscribe(target_account)
            self.subscription_started = True
            yield
        except Exception as e:
            raise exceptions.StartSubscriptionError(target_account, e)
        finally:
            await self.broker.stop()
            self.subscription_started = False

    async def wait_message(self) -> messages.Message | None:
        """
        Returns new messages from broker in real-time mode for the specified account.
        """
        if not self.subscription_started or not self.target_account:
            raise exceptions.SubscriptionNotStarted()

        message_bytes = await self.broker.get_message()
        if message_bytes is None:
            return None

        message = messages.Message.model_validate(orjson.loads(message_bytes))
        message.deliver(self.target_account)

        async with self.uow:
            await self.uow.message_repository.update(message)
            await self.uow.message_repository.commit()

        return message

    def events(self) -> typing.List[cqrs.DomainEvent]:
        return self.uow.get_events()
