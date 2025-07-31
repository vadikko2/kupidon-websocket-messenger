"""
Dont use this module for new attachment types
"""

import datetime
import io
import logging
import typing
import uuid

import cqrs
from cqrs.events import event

from domain import attachments
from infrastructure.helpers.attachments.preprocessors import chain
from service import exceptions, unit_of_work
from service.interfaces import attachment_storage
from service.requests.attachments import upload_attachment
from service.services import storages
from service.validators import chats as chat_validators

logger = logging.getLogger(__name__)
logger.warning(
    "Dont use this module for new attachment types, use service.services.storages instead",
)


class UploadAttachmentHandler(
    cqrs.RequestHandler[
        upload_attachment.UploadAttachment,
        upload_attachment.AttachmentUploaded,
    ],
):
    def __init__(
        self,
        storage: attachment_storage.AttachmentStorage,
        uow: unit_of_work.UoW,
        preprocessing_chains: typing.List[chain.PreprocessingChain],
    ):
        self.storage = storage
        self.uow = uow
        self.preprocessing_chains = preprocessing_chains

    @property
    def events(self) -> typing.List[event.Event]:
        return list(self.uow.get_events())

    async def handle(
        self,
        request: upload_attachment.UploadAttachment,
    ) -> upload_attachment.AttachmentUploaded:
        async with self.uow:
            chat = await self.uow.chat_repository.get(request.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(request.chat_id)
            chat_validators.raise_if_sender_not_in_chat(chat, request.chat_id, request.uploader)

            new_attachment = attachments.Attachment(
                attachment_id=uuid.uuid4(),
                chat_id=request.chat_id,
                uploader=request.uploader,
                filename=request.filename,
                content_type=request.content_type,
            )

            uploading_dt = datetime.datetime.now()
            uploading_file_name = f"{new_attachment.attachment_id}_{request.filename}"
            uploading_path = f"{request.uploader}/{uploading_dt.year}/{uploading_dt.month}"

            urls: typing.List[typing.Text] = [
                await storages.upload_file_to_storage(
                    self.storage,
                    io.BytesIO(request.content),
                    f"{uploading_path}/{uploading_file_name}",
                ),
            ]

            # upload original

            # preprocess
            for preprocessing_chain in self.preprocessing_chains:
                if not preprocessing_chain.content_type == request.content_type:
                    continue

                for (
                    processed_filename,
                    processed_content,
                ) in preprocessing_chain.iterator(
                    io.BytesIO(request.content),
                    uploading_file_name,
                ):
                    # upload preprocessed
                    urls.append(
                        await storages.upload_file_to_storage(
                            self.storage,
                            processed_content,
                            f"{uploading_path}/{processed_filename}",
                        ),
                    )

            # mark as uploaded
            new_attachment.upload(urls=urls, uploaded_dt=uploading_dt)  # pyright: ignore[reportArgumentType]

            # save
            await self.uow.attachment_repository.add(new_attachment)
            await self.uow.commit()

        return upload_attachment.AttachmentUploaded(
            attachment_id=new_attachment.attachment_id,
            urls=urls,  # type: ignore
        )
