import typing

import cqrs
from cqrs.events import event

from service import exceptions, unit_of_work
from service.requests.attachments import get_attachments


class GetAttachmentsHandler(
    cqrs.RequestHandler[get_attachments.GetAttachments, get_attachments.Attachments],
):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self) -> typing.List[event.Event]:
        return []

    async def handle(
        self,
        request: get_attachments.GetAttachments,
    ) -> get_attachments.Attachments:
        async with self.uow:
            chat = await self.uow.chat_repository.get(request.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(chat_id=request.chat_id)
            if not chat.is_participant(request.account_id):
                raise exceptions.ParticipantNotInChat(
                    account_id=request.account_id,
                    chat_id=request.chat_id,
                )

            if not request.attachment_id_filter:
                attachments = await self.uow.attachment_repository.get_all(
                    request.chat_id,
                    request.limit,
                    request.offset,
                    type_filter=request.type_filter,
                    status_filter=request.status_filter,
                )
            else:
                attachments = await self.uow.attachment_repository.get_many(
                    *request.attachment_id_filter,
                    type_filter=request.type_filter,
                    status_filter=request.status_filter,
                )

        return get_attachments.Attachments(
            attachments=[
                get_attachments.AttachmentInfo(
                    chat_id=chat.chat_id,
                    attachment_id=attachment.attachment_id,
                    urls=attachment.urls,  # type: ignore
                    uploaded=attachment.uploaded,
                    content_type=attachment.content_type,
                    meta=attachment.meta or {},
                )
                for attachment in attachments
                if attachment.uploaded
            ],
        )
