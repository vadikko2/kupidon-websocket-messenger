import io
import logging
import typing

import PIL.Image

from domain import attachments
from service.helpers.attachments.image import filename

logging.getLogger("PIL").setLevel(logging.ERROR)


class JPEGPreview100x100AttachmentPreprocessor:
    """Создает уменьшенную версию изображения."""

    size = (100, 100)
    name = "jpg_100x100"
    content_type = attachments.AttachmentType.IMAGE

    def __call__(self, file_object: typing.BinaryIO) -> typing.BinaryIO:
        img = PIL.Image.open(file_object).convert("RGB")
        img.thumbnail(self.size)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)  # Вернуться в начало потока
        return io.BytesIO(img_bytes.getvalue())

    def new_filename(self, file_name: str) -> str:
        return f"{self.name}/{filename.update_filename_jpeg(file_name)}"


class JPEGPreview200x200AttachmentPreprocessor(JPEGPreview100x100AttachmentPreprocessor):
    size = (200, 200)
    name = "jpg_200x200"
