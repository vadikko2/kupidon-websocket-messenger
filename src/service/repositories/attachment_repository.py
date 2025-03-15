import typing
import uuid

import cqrs

from domain import attachments


class AttachmentRepository(typing.Protocol):
    _seen: typing.Set[attachments.Attachment]

    async def add(self, attachment: attachments.Attachment) -> None:
        """Adds new attachment"""
        raise NotImplementedError

    async def get(self, attachment_id: uuid.UUID) -> attachments.Attachment | None:
        """Returns specified attachment"""
        raise NotImplementedError

    async def get_many(
        self,
        *attachment_ids: uuid.UUID,
    ) -> typing.List[attachments.Attachment]:
        """Returns specified attachments"""
        raise NotImplementedError

    async def get_all(
        self,
        chat_id: uuid.UUID,
        limit: int,
        offset: int,
    ) -> typing.List[attachments.Attachment]:
        """Returns all attachments for specified chat"""
        raise NotImplementedError

    def events(self) -> typing.List[cqrs.Event]:
        """
        Returns new domain ecst_events
        """
        raise NotImplementedError
