import cqrs
import orjson

from domain import events, messages
from infrastructure.brokers import messages_broker
from service import exceptions, unit_of_work
from service.requests.ecst_events.messages import message_deleted


class MessageDeletedHandler(cqrs.EventHandler[events.MessageDeleted]):
    def __init__(self, uow: unit_of_work.UoW, broker: messages_broker.MessageBroker):
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
                    cqrs.NotificationEvent(
                        event_name="MessageDeleted",
                        payload=message_deleted.MessageDeletedPayload(
                            chat_id=event.chat_id,
                            message_id=event.message_id,
                        ),
                    ).model_dump(mode="json"),
                ),
            )
