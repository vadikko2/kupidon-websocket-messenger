import abc
import typing


class AttachmentStorage(abc.ABC):
    @abc.abstractmethod
    async def upload(
        self,
        attachment: typing.BinaryIO,
        filename: str,
    ) -> str:
        """Uploads attachment to storage and returns its URL"""
        raise NotImplementedError
