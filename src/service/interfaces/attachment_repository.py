import typing
import uuid

import cqrs

from domain import attachments


class AttachmentRepository(typing.Protocol):
    _seen: set[attachments.Attachment]

    async def add(self, attachment: attachments.Attachment) -> None:
        """Adds new attachment"""
        raise NotImplementedError

    async def get(self, attachment_id: uuid.UUID) -> attachments.Attachment | None:
        """Returns specified attachment"""
        raise NotImplementedError

    async def get_many(
        self,
        *attachment_ids: uuid.UUID,
        type_filter: list[attachments.AttachmentType] | None = None,
        status_filter: list[attachments.AttachmentStatus] | None = None,
    ) -> list[attachments.Attachment]:
        """Returns specified attachments"""
        raise NotImplementedError

    async def get_all(
        self,
        chat_id: uuid.UUID,
        limit: int,
        offset: int,
        type_filter: list[attachments.AttachmentType] | None = None,
        status_filter: list[attachments.AttachmentStatus] | None = None,
    ) -> list[attachments.Attachment]:
        """Returns all attachments for specified chat"""
        raise NotImplementedError

    def events(self) -> list[cqrs.Event]:
        """
        Returns new domain events
        """
        raise NotImplementedError
