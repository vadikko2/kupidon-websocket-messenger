import itertools
import typing

import cqrs

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
        return list(self.uow.get_events())

    async def handle(self, request: get_messages.GetMessages) -> get_messages.Messages:
        async with self.uow:
            chat_history = await self.uow.chat_repository.get_chat_history(
                chat_id=request.chat_id,
                messages_limit=request.messages_limit,
                latest_message_id=request.latest_message_id,
                reverse=request.reverse,
            )

            if chat_history is None:
                raise exceptions.ChatNotFound(request.chat_id)

            if not chat_history.is_participant(request.account):
                raise exceptions.ParticipantNotInChat(
                    request.account,
                    chat_history.chat_id,
                )

            messages: typing.List[get_messages.MessageInfo] = []
            last_read_message = chat_history.last_read_by(request.account)

            for message in sorted(
                chat_history.history,
                key=lambda m: m.created,
            ):
                if message.deleted:
                    continue

                is_message_read = bool(last_read_message) and message.created <= last_read_message.created

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
                        read=is_message_read,
                        created=message.created,
                        updated=message.updated,
                        reply_to=message.reply_to,
                    ),
                )

            if not request.reverse:
                next_message = await self.uow.chat_repository.get_previous_message_id(
                    chat_id=request.chat_id,
                    target_message_id=messages[0].message_id,
                )
                prev_message = (
                    await self.uow.chat_repository.get_next_message_id(
                        chat_id=request.chat_id,
                        target_message_id=(
                            request.latest_message_id if request.latest_message_id else messages[-1].message_id
                        ),
                    )
                    if messages
                    else None
                )

            else:
                next_message = (
                    await self.uow.chat_repository.get_next_message_id(
                        chat_id=request.chat_id,
                        target_message_id=messages[-1].message_id,
                    )
                    if messages
                    else None
                )
                prev_message = await self.uow.chat_repository.get_previous_message_id(
                    chat_id=request.chat_id,
                    target_message_id=(
                        request.latest_message_id if request.latest_message_id else messages[0].message_id
                    ),
                )

        return get_messages.Messages(
            messages=messages,
            next_message_id=next_message.message_id if next_message else None,
            prev_message_id=prev_message.message_id if prev_message else None,
        )


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

            if message.deleted:
                raise exceptions.MessageNotFound(request.message_id)

            return get_messages.MessagePreview(
                message_id=message.message_id,
                chat_id=message.chat_id,
                sender=message.sender,
                content=message.content,
                created=message.created,
            )
