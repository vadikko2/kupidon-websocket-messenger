import datetime
import io
import logging
import typing
import uuid

import cqrs

from domain import attachments, events
from infrastructure.helpers.attachments.processors import chain
from infrastructure.storages import attachment_storage
from service import exceptions, unit_of_work
from service.requests import upload_attachment

logger = logging.getLogger(__name__)


class UploadAttachmentService:
    def __init__(
        self,
        storage: attachment_storage.AttachmentStorage,
        uow: unit_of_work.UoW,
        preprocessor_chains: typing.List[chain.PreprocessingChain] | None = None,
    ):
        self.storage = storage
        self.uow = uow
        self._events = []
        self.preprocessors_chains = preprocessor_chains or []

    async def _upload_file_to_storage(
        self,
        file_object: typing.BinaryIO,
        filename: typing.Text,
    ) -> typing.Text:
        """Uploads file to storage and returns its URL"""
        try:
            url = await self.storage.upload(file_object, filename)
        except Exception as e:
            raise exceptions.AttachmentUploadError(filename, e)

        logger.info(f"Uploaded attachment: {url}")
        return url

    async def handle(
        self,
        chat_id: uuid.UUID,
        uploader: typing.Text,
        content: bytes,
        content_type: attachments.AttachmentType,
        filename: typing.Text,
    ) -> upload_attachment.AttachmentUploaded:
        async with self.uow:
            chat = await self.uow.chat_repository.get(chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(chat_id=chat_id)
            if not chat.is_participant(uploader):
                raise exceptions.ParticipantNotInChat(
                    account_id=uploader,
                    chat_id=chat_id,
                )

            new_attachment_id = uuid.uuid4()
            uploading_dt = datetime.datetime.now()
            uploading_file_name = f"{new_attachment_id}_{filename}"
            uploading_path = f"{uploader}/{uploading_dt.year}/{uploading_dt.month}"

            urls = []

            # upload original
            urls.append(
                await self._upload_file_to_storage(
                    io.BytesIO(content),
                    f"{uploading_path}/{uploading_file_name}",
                ),
            )

            # preprocess
            for processing_chain in self.preprocessors_chains:
                if not processing_chain.content_type == content_type:
                    continue

                for processed_filename, processed_content in processing_chain.iterator(
                    io.BytesIO(content),
                    uploading_file_name,
                ):
                    urls.append(
                        await self._upload_file_to_storage(
                            processed_content,
                            f"{uploading_path}/{processed_filename}",
                        ),
                    )

            # save
            new_attachment = attachments.Attachment(
                attachment_id=new_attachment_id,
                chat_id=chat_id,
                uploader=uploader,
                filename=filename,
                urls=urls,  # type: ignore
                content_type=content_type,
                uploaded=uploading_dt,
            )

            await self.uow.attachment_repository.add(new_attachment)
            await self.uow.commit()

        self._events.append(
            events.NewAttachmentUploaded(
                attachment_id=uuid.uuid4(),
                urls=urls,  # type: ignore
            ),
        )

        return upload_attachment.AttachmentUploaded(
            attachment_id=new_attachment.attachment_id,
            urls=urls,
        )

    def events(self) -> typing.List[cqrs.DomainEvent]:
        return self.uow.get_events() + self._events
