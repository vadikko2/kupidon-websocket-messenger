import abc
import typing


class AttachmentStorage(abc.ABC):
    @abc.abstractmethod
    async def upload(
        self,
        attachment: typing.BinaryIO,
        filename: typing.Text,
    ) -> typing.Text:
        """Uploads attachment to storage and returns its URL"""
        raise NotImplementedError
