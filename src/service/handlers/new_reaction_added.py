import cqrs
import orjson

from domain import events
from infrastructure.brokers import protocol as broker_protocol
from service import events as notification_events, exceptions, unit_of_work


class NewReactionAddedHandler(cqrs.EventHandler[events.NewReactionAdded]):
    def __init__(self, uow: unit_of_work.UoW, broker: broker_protocol.MessageBroker):
        self.uow = uow
        self.broker = broker

    async def handle(self, event: events.NewReactionAdded) -> None:
        async with self.uow:
            message = await self.uow.message_repository.get(event.message_id)

            if message is None:
                raise exceptions.MessageNotFound(event.message_id)

            await self.broker.send_message(
                message.sender,
                orjson.dumps(
                    notification_events.NewReactionAdded(
                        event_name="NewReactionAdded",
                        payload=notification_events.ReactionAddedPayload(
                            chat_id=message.chat_id,
                            message_id=message.message_id,
                            reactor=event.reactor,
                            emoji=event.emoji,
                        ),
                    ).model_dump(mode="json"),
                ),
            )
