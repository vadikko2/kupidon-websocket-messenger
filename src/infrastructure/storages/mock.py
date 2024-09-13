import typing
import urllib.parse

from infrastructure.storages import attachment_storage

_GLOBAL_ATTACHMENTS_STORAGE: typing.Dict[typing.Text, typing.Text] = dict()


class MockAttachmentStorage(attachment_storage.AttachmentStorage):
    async def upload(
        self,
        attachment: typing.BinaryIO,
        filename: typing.Optional[typing.Text] = None,
    ) -> typing.Text:
        url = urllib.parse.urljoin("https://kupidon.storage.mock", filename or "")
        _GLOBAL_ATTACHMENTS_STORAGE[url] = filename or ""
        return url
