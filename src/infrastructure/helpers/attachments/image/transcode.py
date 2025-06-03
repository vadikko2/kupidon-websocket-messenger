import io
import logging
import typing
from infrastructure.helpers.attachments.image import filename

import PIL.Image

from domain.attachments import attachments

logging.getLogger("PIL").setLevel(logging.ERROR)


class JpegTranscodeAttachmentPreprocessor:
    """Переводит изображение в формат JPEG."""

    name = "jpg"
    content_type = attachments.AttachmentType.IMAGE

    def __call__(self, file_object: typing.BinaryIO) -> typing.BinaryIO:
        jpeg_image_bytes = io.BytesIO()
        PIL.Image.open(file_object).convert("RGB").save(jpeg_image_bytes, format="JPEG")
        jpeg_image_bytes.seek(0)
        return io.BytesIO(jpeg_image_bytes.getvalue())

    @staticmethod
    def new_filename(file_name: typing.Text) -> typing.Text:
        return filename.update_filename_jpeg(file_name)
