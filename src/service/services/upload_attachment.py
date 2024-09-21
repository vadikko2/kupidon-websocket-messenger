import asyncio
import datetime
import io
import logging
import typing
import uuid

import cqrs

from domain import attachments, events
from infrastructure.storages import attachment_storage
from service import exceptions, unit_of_work
from service.requests import upload_attachment

logger = logging.getLogger(__name__)


class AttachmentPreprocessor(typing.Protocol):
    name: typing.Text
    content_type: attachments.AttachmentType

    def __call__(self, file_object: typing.BinaryIO) -> typing.BinaryIO:
        raise NotImplementedError

    def update_file_name(self, file_name: typing.Text) -> typing.Text:
        raise NotImplementedError


class PreprocessingChain:
    name: typing.Text

    def __init__(
        self,
        chain_name: typing.Text,
        content_type: attachments.AttachmentType,
        preprocessors: typing.List[AttachmentPreprocessor],
    ):
        if any(filter(lambda p: p.content_type != content_type, preprocessors)):  # type: ignore
            raise ValueError(
                f"All preprocessors should have the same "
                f"content type {content_type}: ({', '.join(map(lambda p: p.content_type, preprocessors))})",
            )
        self.name = chain_name
        self.preprocessors = preprocessors

    def __next__(self) -> AttachmentPreprocessor:
        return next(self._iterator)

    def __iter__(self):
        self._iterator = iter(self.preprocessors)
        return self


class UploadAttachmentService:
    def __init__(
        self,
        storage: attachment_storage.AttachmentStorage,
        uow: unit_of_work.UoW,
        preprocessor_chains: typing.List[PreprocessingChain] | None = None,
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

    async def _process_files(
        self,
        file_object: bytes,
        file_name: typing.Text,
        content_type: attachments.AttachmentType,
    ) -> typing.Dict[typing.Text, typing.BinaryIO]:
        """Applies preprocessing chains"""

        preprocessing_results: typing.Dict[typing.Text, typing.BinaryIO] = {}
        # preprocess
        for chain in self.preprocessors_chains:
            for preprocessor in chain:
                if not preprocessor.content_type == content_type:
                    continue

                new_filename = preprocessor.update_file_name(file_name)
                processing_result = await asyncio.to_thread(
                    preprocessor,
                    io.BytesIO(file_object),
                )

                file_object = result_content = processing_result.read()
                preprocessing_results[new_filename] = io.BytesIO(result_content)

        return preprocessing_results

    async def handle(
        self,
        chat_id: uuid.UUID,
        uploader: typing.Text,
        file_object: typing.BinaryIO,
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

            content = file_object.read()
            # preprocess
            procession_results = await self._process_files(
                content,
                uploading_file_name,
                content_type,
            )

            # upload original
            urls.append(
                await self._upload_file_to_storage(
                    io.BytesIO(content),
                    f"{uploading_path}/{uploading_file_name}",
                ),
            )
            # upload preprocessed
            for new_file_name, result in procession_results.items():
                urls.append(
                    await self._upload_file_to_storage(
                        result,
                        f"{uploading_path}/{new_file_name}",
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
