import datetime

import cqrs
import pydantic


class NewMessageAdded(cqrs.DomainEvent, frozen=True):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4

    sender: str


class NewParticipantAdded(cqrs.DomainEvent, frozen=True):
    chat_id: pydantic.UUID4
    account_id: str
    invited_by: str


class MessageRead(cqrs.DomainEvent, frozen=True):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4
    reader_id: str
    read_at: datetime.datetime


class MessageUpdated(cqrs.DomainEvent, frozen=True):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4
    message_sender: str
    message_content: str | None
    message_attachments: list[pydantic.UUID4]


class MessageDeleted(cqrs.DomainEvent, frozen=True):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4
    message_sender: str


class NewAttachmentUploaded(cqrs.DomainEvent, frozen=True):
    attachment_id: pydantic.UUID4
    urls: list[str]


class AttachmentSent(cqrs.DomainEvent, frozen=True):
    message_id: pydantic.UUID4
    attachment_id: pydantic.UUID4


class MessageReacted(cqrs.DomainEvent, frozen=True):
    reaction_id: pydantic.UUID4
    reactor: str
    message_id: pydantic.UUID4
    emoji: str


class MessageUnreacted(cqrs.DomainEvent, frozen=True):
    reaction_id: pydantic.UUID4
    message_id: pydantic.UUID4


class TappingInChat(cqrs.DomainEvent, frozen=True):
    chat_id: pydantic.UUID4
    account_id: str
