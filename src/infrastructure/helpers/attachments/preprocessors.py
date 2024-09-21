import io
import pathlib
import typing

import PIL.Image

from domain import attachments


def update_filename_jpeg(file_name: typing.Text) -> typing.Text:
    return str(pathlib.Path(file_name).with_suffix(".jpg"))


class JpegTranscodeAttachmentPreprocessor:
    """Переводит изображение в формат JPEG."""

    name = "jpg"
    content_type = attachments.AttachmentType.IMAGE

    def __call__(self, file_object: typing.BinaryIO) -> typing.BinaryIO:
        jpeg_image_bytes = io.BytesIO()
        PIL.Image.open(file_object).convert("RGB").save(jpeg_image_bytes, format="JPEG")
        jpeg_image_bytes.seek(0)
        return io.BytesIO(jpeg_image_bytes.getvalue())

    def update_file_name(self, file_name: typing.Text) -> typing.Text:
        return update_filename_jpeg(file_name)


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

    def update_file_name(self, file_name: typing.Text) -> typing.Text:
        return f"{self.name}/{update_filename_jpeg(file_name)}"


class JPEGPreview200x200AttachmentPreprocessor(
    JPEGPreview100x100AttachmentPreprocessor,
):
    size = (200, 200)
    name = "jpg_200x200"
