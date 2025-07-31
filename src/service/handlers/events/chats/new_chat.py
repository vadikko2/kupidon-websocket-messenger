import typing

import cqrs
import orjson

from domain import events
from infrastructure.brokers import messages_broker
from service import exceptions, unit_of_work
from service.requests.ecst_events.chats import new_chat
from service.validators import chats as chat_validators


class AddedIntoNewChatHandler(cqrs.EventHandler[events.NewParticipantAdded]):
    def __init__(self, uow: unit_of_work.UoW, broker: messages_broker.MessageBroker):
        self.uow = uow
        self.broker = broker

    async def handle(self, event: events.NewParticipantAdded) -> None:
        async with self.uow:
            chat = await self.uow.chat_repository.get(event.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(event.chat_id)
            chat_validators.raise_if_sender_not_in_chat(
                chat,
                event.chat_id,
                event.account_id,
            )

            chat_added_event: typing.ByteString = orjson.dumps(
                cqrs.NotificationEvent[new_chat.AddedIntoChatPayload](
                    event_name="AddedIntoChat",
                    payload=new_chat.AddedIntoChatPayload(
                        chat_id=event.chat_id,
                        account_id=event.account_id,
                        invited_by=event.invited_by,
                    ),
                ).model_dump(mode="json"),
            )
            await self.broker.send_message(
                event.account_id,
                chat_added_event,
            )
