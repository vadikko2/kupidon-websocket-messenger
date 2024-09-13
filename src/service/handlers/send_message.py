import logging
import typing

import cqrs
from cqrs.events import event

from domain import messages
from service import exceptions, unit_of_work
from service.requests import send_message

logger = logging.getLogger(__name__)


class SendMessageHandler(
    cqrs.RequestHandler[send_message.SendMessage, send_message.MessageSent],
):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow
        self._events = []

    @property
    def events(self) -> typing.List[event.Event]:
        return self._events

    async def handle(
        self,
        request: send_message.SendMessage,
    ) -> send_message.MessageSent:
        async with self.uow:
            chat = await self.uow.chat_repository.get(request.chat_id)

            if chat is None:
                raise exceptions.ChatNotFound(request.chat_id)

            if not chat.is_participant(request.sender):
                raise exceptions.ParticipantNotInChat(
                    request.sender,
                    chat.chat_id,
                )

            attachments = await self.uow.attachment_repository.get_many(
                *request.attachments,
            )
            for attachment in attachments:
                if attachment.chat_id != request.chat_id:
                    raise exceptions.AttachmentNotForChat(
                        attachment.attachment_id,
                        request.chat_id,
                    )

            attachment_difference = set(
                [att.attachment_id for att in attachments],
            ).difference(request.attachments)

            logger.error(
                f"Requested and read attachments has difference: {','.join(map(str, attachment_difference))}",
            )

            if len(attachment_difference):
                raise exceptions.AttachmentNotFound(attachment_difference.pop())

            new_message = messages.Message(
                chat_id=request.chat_id,
                sender=request.sender,
                reply_to=request.reply_to,
                content=request.content,
                attachments=attachments,
            )

            chat.add_message(new_message)

            await self.uow.message_repository.add(new_message)
            await self.uow.commit()

        self._events += self.uow.get_events()

        return send_message.MessageSent(
            message_id=new_message.message_id,
            created=new_message.created,
        )
