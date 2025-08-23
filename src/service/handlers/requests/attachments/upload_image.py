import datetime
import io
import typing
import uuid

import cqrs
from cqrs.events import event

from domain import attachments
from infrastructure.helpers.attachments.image import preview, transcode
from service import exceptions
from service.interfaces import unit_of_work
from service.interfaces import attachment_storage
from service.requests.attachments import upload_image
from service.services import storages
from service.validators import chats as chat_validators


class UploadImageHandler(cqrs.RequestHandler[upload_image.UploadImage, upload_image.ImageUploaded]):
    def __init__(
        self,
        storage: attachment_storage.AttachmentStorage,
        uow: unit_of_work.UoW,
    ):
        self.storage = storage
        self.uow = uow

    @property
    def events(self) -> typing.List[event.Event]:
        return []

    async def handle(self, request: upload_image.UploadImage) -> upload_image.ImageUploaded:
        async with self.uow:
            chat = await self.uow.chat_repository.get(request.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(request.chat_id)
            chat_validators.raise_if_sender_not_in_chat(
                chat,
                request.chat_id,
                request.uploader,
            )

            transcode_processor = transcode.JpegTranscodeAttachmentPreprocessor()
            preview_100x100_processor = preview.JPEGPreview100x100AttachmentPreprocessor()
            preview_200x200_processor = preview.JPEGPreview200x200AttachmentPreprocessor()

            transcode_io = transcode_processor(io.BytesIO(request.content)).read()

            attachment_id = uuid.uuid4()
            uploading_dt = datetime.datetime.now()
            uploading_file_name = str(attachment_id)
            uploading_path = f"{request.uploader}/{uploading_dt.year}/{uploading_dt.month}"

            # upload original
            urls: typing.List[typing.Text] = [
                await storages.upload_file_to_storage(
                    self.storage,
                    io.BytesIO(transcode_io),
                    f"{uploading_path}/{transcode_processor.new_filename(uploading_file_name)}",
                ),
            ]

            # upload preview

            preview_100x100_url = await storages.upload_file_to_storage(
                self.storage,
                preview_100x100_processor(io.BytesIO(transcode_io)),
                f"{uploading_path}/{preview_100x100_processor.new_filename(uploading_file_name)}",
            )

            preview_200x200_url = await storages.upload_file_to_storage(
                self.storage,
                preview_200x200_processor(io.BytesIO(transcode_io)),
                f"{uploading_path}/{preview_200x200_processor.new_filename(uploading_file_name)}",
            )

            new_attachment = attachments.Attachment(
                attachment_id=uuid.uuid4(),
                chat_id=request.chat_id,
                uploader=request.uploader,
                content_type=attachments.AttachmentType.IMAGE,
            )

            new_attachment.upload(
                urls=urls,
                uploaded_dt=uploading_dt,
                meta=attachments.ImageMeta(
                    width=request.width,
                    height=request.height,
                    url_100x100=preview_100x100_url,
                    url_200x200=preview_200x200_url,
                    image_type=attachments.ImageTypes.JPEG,
                ).model_dump(mode="python"),
            )

            await self.uow.attachment_repository.add(new_attachment)

            await self.uow.commit()

        return upload_image.ImageUploaded(
            attachment_id=new_attachment.attachment_id,
            attachment_urls=[
                *urls,
                preview_100x100_url,
                preview_200x200_url,
            ],
        )
