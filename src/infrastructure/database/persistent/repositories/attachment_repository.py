import abc
import typing
import uuid

import cqrs

from domain import attachments


class AttachmentRepository(abc.ABC):
    _seen: typing.Set[attachments.Attachment]

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

    @abc.abstractmethod
    async def commit(self):
        """Commits changes"""
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self):
        """Rollbacks changes"""
        raise NotImplementedError

    def events(self) -> typing.List[cqrs.Event]:
        """
        Returns new domain ecst_events
        """
        new_events = []
        for attachment in self._seen:
            while attachment.event_list:
                new_events.append(attachment.event_list.pop())
        return new_events
