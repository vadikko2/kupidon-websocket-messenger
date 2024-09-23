import contextlib
import logging
import typing

from infrastructure.brokers import messages_broker
from service import exceptions

logger = logging.getLogger(__name__)


class SubscriptionService:
    """
    Subscription service.
    """

    def __init__(
        self,
        broker: messages_broker.MessageBroker,
    ) -> None:
        self.broker = broker
        self.subscription_started = False
        self.target_account: typing.Text | None = None

    @contextlib.asynccontextmanager
    async def start_subscription(self, target_account: typing.Text):
        """
        Opens subscription to broker for the specified account.
        """
        try:
            self.target_account = target_account
            await self.broker.start()
            await self.broker.subscribe(target_account)
            self.subscription_started = True
            yield
        except Exception as e:
            raise exceptions.StartSubscriptionError(target_account, e)
        finally:
            await self.broker.stop()
            self.subscription_started = False
            self.target_account = None

    async def wait_events(self) -> bytes | None:
        """
        Returns new events from broker in real-time mode for the specified account.
        """
        if not self.subscription_started or not self.target_account:
            raise exceptions.SubscriptionNotStarted()

        event_bytes = await self.broker.get_message()
        if event_bytes is None:
            return None

        logger.debug(f"Got event from broker: {event_bytes}")
        return event_bytes
