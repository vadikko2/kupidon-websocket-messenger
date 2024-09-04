import datetime
import enum
import logging
import typing
import uuid

import cqrs
import pydantic

from domain import events

logger = logging.getLogger(__name__)


class MessageStatus(enum.IntEnum):
    """
    Message statuses
    """

    SENT = 1
    RECEIVED = 2
    DELIVERED = 3
    READ = 4
    DELETED = 5


class AttachmentType(enum.StrEnum):
    """
    Attachment types
    """

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"


class Attachment(pydantic.BaseModel, frozen=True):
    """
    Attachment entity
    """

    attachment_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
    created: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    url: pydantic.AnyUrl
    name: typing.Optional[typing.Text] = pydantic.Field(default=None, max_length=100)
    content_type: AttachmentType

    def __hash__(self):
        return str(hash(self.attachment_id))


class Message(pydantic.BaseModel):
    """
    Message entity
    """

    message_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4, frozen=True)
    chat_id: uuid.UUID = pydantic.Field(frozen=True)

    sender: typing.Text = pydantic.Field(frozen=True)

    reply_to: typing.Optional[uuid.UUID] = pydantic.Field(default=None, frozen=True)

    content: typing.Text = pydantic.Field(frozen=True)
    attachments: typing.List[Attachment] = pydantic.Field(
        default_factory=list,
        max_length=5,
        frozen=True,
    )
    status: MessageStatus = pydantic.Field(default=MessageStatus.SENT)

    created: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now,
        frozen=True,
    )
    updated: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now,
    )

    event_list: typing.List[cqrs.DomainEvent] = pydantic.Field(default_factory=list)

    def deliver(self, receiver: typing.Text) -> None:
        self.status = MessageStatus.DELIVERED
        self.updated = datetime.datetime.now()
        logger.debug(f"Message {self.message_id} delivered by {receiver}")
        self.event_list.append(
            events.MessageDelivered(
                chat_id=self.chat_id,
                message_id=self.message_id,
                receiver_id=receiver,
            ),
        )

    def receive(self, receiver: typing.Text) -> None:
        self.status = MessageStatus.RECEIVED
        self.updated = datetime.datetime.now()
        logger.debug(f"Message {self.message_id} received by {receiver}")
        self.event_list.append(
            events.MessageReceived(
                chat_id=self.chat_id,
                message_id=self.message_id,
                receiver_id=receiver,
            ),
        )

    def read(self, reader: typing.Text) -> None:
        self.status = MessageStatus.READ
        self.updated = datetime.datetime.now()
        logger.debug(f"Message {self.message_id} read by {reader}")
        self.event_list.append(
            events.MessageRead(
                chat_id=self.chat_id,
                message_id=self.message_id,
                reader_id=reader,
            ),
        )

    def delete(self) -> None:
        self.status = MessageStatus.DELETED
        self.updated = datetime.datetime.now()
        logger.debug(f"Message {self.message_id} deleted")
        self.event_list.append(
            events.MessageDeleted(chat_id=self.chat_id, message_id=self.message_id),
        )

    def get_events(self) -> typing.List[cqrs.DomainEvent]:
        """
        Returns new domain events
        """
        new_events = []
        while self.event_list:
            new_events.append(self.event_list.pop())
        return new_events

    def __hash__(self):
        return hash(self.message_id)
