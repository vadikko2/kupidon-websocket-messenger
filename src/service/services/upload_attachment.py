import logging
import typing
import uuid

import cqrs

from domain import attachments, events
from infrastructure.storages import attachment_storage
from service import exceptions, unit_of_work
from service.requests import upload_attachment

logger = logging.getLogger(__name__)


class UploadAttachmentService:
    def __init__(
        self,
        storage: attachment_storage.AttachmentStorage,
        uow: unit_of_work.UoW,
    ):
        self.storage = storage
        self.uow = uow
        self._events = []

    async def handle(
        self,
        chat_id: uuid.UUID,
        uploader: typing.Text,
        file_object: typing.BinaryIO,
        content_type: attachments.AttachmentType,
        filename: typing.Optional[typing.Text] = None,
    ) -> upload_attachment.AttachmentUploaded:
        url = await self.storage.upload(file_object, filename)
        logger.info(f"Uploaded attachment: {url}")

        new_attachment = attachments.Attachment(
            attachment_id=uuid.uuid4(),
            chat_id=chat_id,
            uploader=uploader,
            filename=filename,
            url=url,  # type: ignore
            content_type=content_type,
        )

        async with self.uow:
            chat = await self.uow.chat_repository.get(chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(chat_id=chat_id)
            if not chat.is_participant(uploader):
                raise exceptions.ParticipantNotInChat(
                    account_id=uploader,
                    chat_id=chat_id,
                )

            await self.uow.attachment_repository.add(new_attachment)
            await self.uow.commit()

        self._events.append(
            events.NewAttachmentUploaded(
                attachment_id=uuid.uuid4(),
                url=url,  # type: ignore
            ),
        )

        return upload_attachment.AttachmentUploaded(
            attachment_id=new_attachment.attachment_id,
            url=new_attachment.url,
        )

    def events(self) -> typing.List[cqrs.DomainEvent]:
        return self.uow.get_events() + self._events
