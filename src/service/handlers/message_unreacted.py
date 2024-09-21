import cqrs
import orjson

from domain import events, messages
from infrastructure.brokers import messages_broker
from service import events as notification_events, exceptions, unit_of_work


class MessageUnreactedHandler(cqrs.EventHandler[events.MessageUnreacted]):
    def __init__(self, uow: unit_of_work.UoW, broker: messages_broker.MessageBroker):
        self.uow = uow
        self.broker = broker

    async def handle(self, event: events.MessageUnreacted) -> None:
        async with self.uow:
            message = await self.uow.message_repository.get(event.message_id)

            if message is None or message.status == messages.MessageStatus.DELETED:
                raise exceptions.MessageNotFound(event.message_id)

            await self.broker.send_message(
                message.sender,
                orjson.dumps(
                    notification_events.MessageUnreactedECST(
                        event_name="MessageUnreacted",
                        payload=notification_events.MessageUnreactedPayload(
                            chat_id=message.chat_id,
                            message_id=message.message_id,
                            reaction_id=event.reaction_id,
                        ),
                    ).model_dump(mode="json"),
                ),
            )
