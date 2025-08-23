import datetime
import hashlib
import io
import logging
import typing
import uuid

import cqrs

from domain import attachments
from service import exceptions
from service.interfaces import attachment_storage, unit_of_work
from service.requests.attachments import upload_circle
from service.services import storages
from service.validators import chats as chat_validators

logger = logging.getLogger(__name__)


class UploadCircleHandler(cqrs.RequestHandler[upload_circle.UploadCircle, upload_circle.CircleUploaded]):
    def __init__(
        self,
        storage: attachment_storage.AttachmentStorage,
        uow: unit_of_work.UoW,
    ):
        self.storage = storage
        self.uow = uow

    @property
    def events(self) -> typing.List[cqrs.Event]:
        return []

    async def handle(self, request: upload_circle.UploadCircle) -> upload_circle.CircleUploaded:
        async with self.uow:
            chat = await self.uow.chat_repository.get(request.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(request.chat_id)
            chat_validators.raise_if_sender_not_in_chat(chat, request.chat_id, request.uploader)

            logger.info(
                f"Processing circle file, size: "
                f"{len(request.content)} bytes, md5: {hashlib.md5(request.content).hexdigest()}",
            )

            attachment_uuid = uuid.uuid4()
            uploading_dt = datetime.datetime.now()
            uploading_file_name = f"{attachment_uuid}.{request.circle_format}"
            uploading_path = f"{request.uploader}/{uploading_dt.year}/{uploading_dt.month}"

            new_attachment = attachments.Attachment(
                attachment_id=attachment_uuid,
                chat_id=request.chat_id,
                uploader=request.uploader,
                content_type=attachments.AttachmentType.CIRCLE,
            )
            url = await storages.upload_file_to_storage(
                self.storage,
                io.BytesIO(request.content),
                f"{uploading_path}/{uploading_file_name}",
            )

            new_attachment.upload(
                urls=[url],
                uploaded_dt=uploading_dt,
                meta=attachments.CircleAttachmentMeta(
                    circle_type=attachments.CircleTypes(request.circle_format),
                    duration_seconds=request.duration_milliseconds,
                    duration_milliseconds=request.duration_milliseconds,
                ).model_dump(mode="python"),
            )

            await self.uow.attachment_repository.add(new_attachment)
            await self.uow.commit()

            return upload_circle.CircleUploaded(
                attachment_id=new_attachment.attachment_id,
                attachment_url=url,
            )
