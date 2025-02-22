import itertools
import typing

import cqrs

from domain import messages as messages_entity
from service import exceptions, unit_of_work
from service.requests.attachments import get_attachments
from service.requests.messages import get_messages


class GetMessagesHandler(
    cqrs.RequestHandler[get_messages.GetMessages, get_messages.Messages],
):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self):
        return self.uow.get_events()

    async def handle(self, request: get_messages.GetMessages) -> get_messages.Messages:
        async with self.uow:
            chat_history = await self.uow.chat_repository.get_chat_history(
                chat_id=request.chat_id,
                messages_limit=request.messages_limit,
                latest_message_id=request.latest_message_id,
            )

            if chat_history is None:
                raise exceptions.ChatNotFound(request.chat_id)

            if not chat_history.is_participant(request.account):
                raise exceptions.ParticipantNotInChat(
                    request.account,
                    chat_history.chat_id,
                )

            messages: typing.List[get_messages.MessageInfo] = []

            for message in chat_history.history:
                if message.status == messages_entity.MessageStatus.DELETED:
                    continue
                message_reactions = []
                message_attachments = []

                for emoji, group in itertools.groupby(
                    message.reactions,
                    key=lambda r: r.emoji,
                ):
                    message_reactions.append(
                        get_messages.ReactionsUnderMessage(
                            message_id=message.message_id,
                            emoji=emoji,
                            count=len(list(group)),
                        ),
                    )
                for attach in message.attachments:
                    message_attachments.append(
                        get_attachments.Attachment(
                            attachment_id=attach.attachment_id,
                            urls=attach.urls,
                            uploaded=attach.uploaded,
                            content_type=attach.content_type,
                        ),
                    )

                messages.append(
                    get_messages.MessageInfo(
                        chat_id=message.chat_id,
                        message_id=message.message_id,
                        sender=message.sender,
                        content=message.content,
                        attachments=message_attachments,
                        reactions=message_reactions,
                        status=message.status,
                        created=message.created,
                        updated=message.updated,
                    ),
                )

        return get_messages.Messages(messages=messages)
