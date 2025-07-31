import cqrs

from service import exceptions, unit_of_work
from service.requests.messages import update_message as update_message_request
from service.validators import (
    attachments as attachment_validators,
    chats as chat_validators,
    messages as message_validators,
)


class UpdateMessageHandler(
    cqrs.RequestHandler[
        update_message_request.UpdateMessage,
        update_message_request.MessageUpdated,
    ],
):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self):
        return list(self.uow.get_events())

    async def handle(
        self,
        request: update_message_request.UpdateMessage,
    ) -> update_message_request.MessageUpdated:
        async with self.uow:
            chat = await self.uow.chat_repository.get(request.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(request.chat_id)
            chat_validators.raise_if_sender_not_in_chat(chat, request.chat_id, request.updater)

            # Check attachments
            attachments = await self.uow.attachment_repository.get_many(*request.attachments)
            attachment_validators.raise_if_attachment_not_found(attachments, request.attachments)
            attachment_validators.raise_if_attachment_not_for_chat(attachments, request.chat_id)
            attachment_validators.raise_if_attachment_not_for_sender(attachments, request.updater)

            message = await self.uow.message_repository.get(request.message_id)
            if not message:
                raise exceptions.MessageNotFound(request.message_id)
            message_validators.raise_if_message_deleted(message)

            message.update(
                content=request.content,
                attachments=attachments,
            )

            await self.uow.message_repository.update(message)
            await self.uow.commit()

        return update_message_request.MessageUpdated(
            message_id=message.message_id,
            chat_id=message.chat_id,
            updated_at=message.updated,
        )
