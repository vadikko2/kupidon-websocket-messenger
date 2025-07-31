import itertools
import typing

import cqrs

from service import exceptions, unit_of_work
from service.requests.attachments import get_attachments
from service.requests.messages import get_messages
from service.validators import chats as chat_validators, messages as message_validators


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
                reverse=not request.reverse,
            )

            if chat_history is None:
                raise exceptions.ChatNotFound(request.chat_id)
            chat_validators.raise_if_sender_not_in_chat(
                chat_history,
                request.chat_id,
                request.account,
            )

            messages: typing.List[get_messages.MessageInfo] = []
            last_read_message = chat_history.last_read_by(request.account)

            for message in chat_history.history:
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
                        attachment_status=attach.status,
                        chat_id=attach.chat_id,
                        urls=attach.urls,  # pyright: ignore[reportArgumentType]
                        uploaded=attach.uploaded,
                        content_type=attach.content_type,
                        meta=attach.meta or {},
                    )
                    for attach in message.attachments
                ]

                replied_message_info: typing.Optional[get_messages.MessagePreview] = None
                if message.reply_to:
                    replied_message = await self.uow.message_repository.get(message.reply_to)
                    if replied_message is not None:
                        replied_message_info = get_messages.MessagePreview(
                            message_id=replied_message.message_id,
                            chat_id=replied_message.chat_id,
                            sender=replied_message.sender,
                            content=replied_message.content,
                            created=replied_message.created,
                        )

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
                        reply_to=replied_message_info,
                    ),
                )

            messages.sort(key=lambda m: m.created, reverse=True)

            next_message = (
                await self.uow.chat_repository.get_next_message_id(
                    chat_id=request.chat_id,
                    target_message_id=messages[0].message_id,
                )
                if messages
                else None
            )
            prev_message = (
                await self.uow.chat_repository.get_previous_message_id(
                    chat_id=request.chat_id,
                    target_message_id=messages[-1].message_id,
                )
                if messages
                else None
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
            message = await self.uow.message_repository.get(message_id=request.message_id)
            if not message:
                raise exceptions.MessageNotFound(request.message_id)
            message_validators.raise_if_message_deleted(message)

            chat = await self.uow.chat_repository.get(chat_id=message.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(message.chat_id)
            chat_validators.raise_if_sender_not_in_chat(chat, message.chat_id, request.account)

            return get_messages.MessagePreview(
                message_id=message.message_id,
                chat_id=message.chat_id,
                sender=message.sender,
                content=message.content,
                created=message.created,
            )
