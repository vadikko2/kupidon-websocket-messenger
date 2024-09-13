import abc
import typing
import uuid

from domain import attachments


class AttachmentRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, attachment: attachments.Attachment) -> None:
        """Adds new attachment"""
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, attachment_id: uuid.UUID) -> attachments.Attachment | None:
        """Returns specified attachment"""
        raise NotImplementedError

    @abc.abstractmethod
    async def get_many(
        self,
        *attachment_ids: uuid.UUID,
    ) -> typing.List[attachments.Attachment]:
        """Returns specified attachments"""
        raise NotImplementedError

    @abc.abstractmethod
    async def get_all(
        self,
        chat_id: uuid.UUID,
        limit: int,
        offset: int,
    ) -> typing.List[attachments.Attachment]:
        """Returns all attachments for specified chat"""
        raise NotImplementedError
