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

            for message in sorted(
                chat_history.history,
                key=lambda m: m.created,
                reverse=True,
            ):
                if message.status == messages_entity.MessageStatus.DELETED:
                    continue

                message_reactions = [
                    get_messages.ReactionsUnderMessage(
                        message_id=message.message_id,
                        emoji=emoji,
                        count=len(list(group)),
                    )
                    for emoji, group in itertools.groupby(
                        message.reactions,
                        key=lambda r: r.emoji,
                    )
                ]

                message_attachments = [
                    get_attachments.AttachmentInfo(
                        attachment_id=attach.attachment_id,
                        chat_id=attach.chat_id,
                        urls=attach.urls,
                        uploaded=attach.uploaded,
                        content_type=attach.content_type,
                    )
                    for attach in message.attachments
                ]

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


class GetMessagePreviewHandler(
    cqrs.RequestHandler[get_messages.GetMessagePreview, get_messages.MessagePreview],
):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self):
        return []

    async def handle(
        self,
        request: get_messages.GetMessagePreview,
    ) -> get_messages.MessagePreview:
        async with self.uow:
            message = await self.uow.message_repository.get(
                message_id=request.message_id,
            )
            if not message:
                raise exceptions.MessageNotFound(request.message_id)

            chat = await self.uow.chat_repository.get(
                chat_id=message.chat_id,
            )

            if not chat:
                raise exceptions.ChatNotFound(message.chat_id)

            if request.account not in chat.participants:
                raise exceptions.ParticipantNotInChat(
                    request.account,
                    chat.chat_id,
                )

            return get_messages.MessagePreview(
                message_id=message.message_id,
                chat_id=message.chat_id,
                sender=message.sender,
                content=message.content,
                status=message.status,
                created=message.created,
            )
