import typing
import urllib.parse

from infrastructure import settings
from infrastructure.storages import attachment_storage

_GLOBAL_ATTACHMENTS_STORAGE: typing.Dict[typing.Text, typing.Text] = dict()


class MockAttachmentStorage(attachment_storage.AttachmentStorage):
    async def upload(
        self,
        attachment: typing.BinaryIO,
        filename: typing.Text,
    ) -> typing.Text:
        url = settings.s3_settings.ENDPOINT_URL + "/" "mock" + "/" + urllib.parse.quote(
            filename,
        )

        if url in _GLOBAL_ATTACHMENTS_STORAGE:
            raise KeyError(f"Attachment {filename} already exists")

        _GLOBAL_ATTACHMENTS_STORAGE[url] = filename
        return url
