import logging

import cqrs

from domain import messages
from service import exceptions, unit_of_work
from service.requests.messages import send_message
from service.validators import attachments as attachment_validators, chats as chat_validators

logger = logging.getLogger(__name__)


class SendMessageHandler(
    cqrs.RequestHandler[send_message.SendMessage, send_message.MessageSent],
):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self):
        return list(self.uow.get_events())

    async def handle(
        self,
        request: send_message.SendMessage,
    ) -> send_message.MessageSent:
        async with self.uow:
            chat = await self.uow.chat_repository.get(request.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(request.chat_id)
            chat_validators.raise_if_sender_not_in_chat(
                chat,
                request.chat_id,
                request.sender,
            )

            # Check attachments
            attachments = await self.uow.attachment_repository.get_many(
                *request.attachments,
            )
            attachment_validators.raise_if_attachment_not_found(attachments, request.attachments)
            attachment_validators.raise_if_attachment_not_for_chat(attachments, request.chat_id)
            attachment_validators.raise_if_attachment_not_for_sender(attachments, request.sender)

            # Create message
            new_message = messages.Message(
                chat_id=request.chat_id,
                sender=request.sender,
                reply_to=request.reply_to,
                content=request.content,
                attachments=attachments,
            )

            chat.add_message(new_message)

            await self.uow.message_repository.add(new_message)
            await self.uow.chat_repository.update(chat)
            await self.uow.commit()

        return send_message.MessageSent(
            message_id=new_message.message_id,
            created=new_message.created,
        )
