import datetime
import hashlib
import io
import logging
import tempfile
import uuid

import cqrs

import settings
from domain import attachments
from service import exceptions
from service.helpers.attachments import upload_attachment
from service.helpers.attachments.audio import histogram
from service.interfaces import attachment_storage, unit_of_work
from service.models.attachments import upload_voice
from service.validators import chats as chat_validators

logger = logging.getLogger(__name__)

app_settings = settings.App()


class UploadVoiceHandler(cqrs.RequestHandler[upload_voice.UploadVoice, upload_voice.VoiceUploaded]):
    def __init__(
        self,
        storage: attachment_storage.AttachmentStorage,
        uow: unit_of_work.UoW,
    ):
        self.storage = storage
        self.uow = uow

    @property
    def events(self) -> list[cqrs.Event]:
        return []

    async def handle(self, request: upload_voice.UploadVoice) -> upload_voice.VoiceUploaded:
        async with self.uow:
            chat = await self.uow.chat_repository.get(request.chat_id)
            if chat is None:
                raise exceptions.ChatNotFound(request.chat_id)
            chat_validators.raise_if_sender_not_in_chat(chat, request.chat_id, request.uploader)

            decoders_map = {
                "mp3": histogram.mp3_decoder,
            }

            if request.voice_format not in decoders_map:
                raise exceptions.UnsupportedVoiceFormat(request.voice_format)

            logger.info(
                f"Processing voice file, size: "
                f"{len(request.content)} bytes, md5: {hashlib.md5(request.content).hexdigest()}",
            )

            attachment_uuid = uuid.uuid4()
            uploading_dt = datetime.datetime.now()
            uploading_file_name = f"{attachment_uuid}.{request.voice_format}"
            uploading_path = f"{request.uploader}/{uploading_dt.year}/{uploading_dt.month}"

            # Используем временный файл с автоматическим удалением
            with tempfile.NamedTemporaryFile(suffix=f".{request.voice_format}", delete=True) as tmp_file:
                tmp_file.write(request.content)
                tmp_file.flush()  # Убедимся, что данные записаны на диск

                try:
                    voice_histogram = histogram.AudioToHistogram(decoders_map[request.voice_format])(tmp_file.name)
                except (histogram.HistogramExtractionError, histogram.DecodeVoiceError) as e:
                    raise exceptions.AttachmentUploadError(e)

                new_attachment = attachments.Attachment(
                    attachment_id=attachment_uuid,
                    chat_id=request.chat_id,
                    uploader=request.uploader,
                    content_type=attachments.AttachmentType.VOICE,
                )

                # Перемещаем указатель в начало для чтения
                tmp_file.seek(0)
                url = await upload_attachment.upload_file_to_storage(
                    self.storage,
                    io.BytesIO(request.content),
                    f"{uploading_path}/{uploading_file_name}",
                )

                new_attachment.upload(
                    urls=[url],
                    uploaded_dt=uploading_dt,
                    meta=attachments.VoiceAttachmentMeta(
                        voice_type=attachments.VoiceTypes(request.voice_format),
                        amplitudes=voice_histogram,
                        duration_seconds=request.duration_milliseconds,
                        duration_milliseconds=request.duration_milliseconds,
                    ).model_dump(mode="python"),
                )

                await self.uow.attachment_repository.add(new_attachment)
                await self.uow.commit()

                return upload_voice.VoiceUploaded(
                    attachment_id=new_attachment.attachment_id,
                    attachment_url=url,
                    amplitudes=voice_histogram,
                )
