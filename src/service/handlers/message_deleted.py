import cqrs
import orjson

from domain import events, messages
from infrastructure.brokers import protocol as broker_protocol
from service import events as notification_events, exceptions, unit_of_work


class MessageDeletedHandler(cqrs.EventHandler[events.MessageDeleted]):
    def __init__(self, uow: unit_of_work.UoW, broker: broker_protocol.MessageBroker):
        self.uow = uow
        self.broker = broker

    async def handle(self, event: events.MessageDeleted) -> None:
        async with self.uow:
            message = await self.uow.message_repository.get(event.message_id)

            if message is not None and message.status != messages.MessageStatus.DELETED:
                raise exceptions.MessageNotDeleted(event.message_id)

            await self.broker.send_message(
                event.message_sender,
                orjson.dumps(
                    notification_events.MessageDeletedECST(
                        event_name="MessageDeleted",
                        payload=notification_events.MessageDeletedPayload(
                            chat_id=event.chat_id,
                            message_id=event.message_id,
                        ),
                    ).model_dump(mode="json"),
                ),
            )
