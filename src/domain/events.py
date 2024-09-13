import typing
import uuid

import cqrs
import pydantic


class NewMessageAdded(cqrs.DomainEvent, frozen=True):
    chat_id: uuid.UUID
    message_id: uuid.UUID


class NewParticipantAdded(cqrs.DomainEvent, frozen=True):
    chat_id: uuid.UUID
    account_id: typing.Text


class MessageRead(cqrs.DomainEvent, frozen=True):
    chat_id: uuid.UUID
    message_id: uuid.UUID
    reader_id: typing.Text


class MessageReceived(cqrs.DomainEvent, frozen=True):
    chat_id: uuid.UUID
    message_id: uuid.UUID
    receiver_id: typing.Text


class MessageDeleted(cqrs.DomainEvent, frozen=True):
    chat_id: uuid.UUID
    message_id: uuid.UUID


class MessageDelivered(cqrs.DomainEvent, frozen=True):
    chat_id: uuid.UUID
    message_id: uuid.UUID
    receiver_id: typing.Text


class NewAttachmentUploaded(cqrs.DomainEvent, frozen=True):
    attachment_id: uuid.UUID
    url: pydantic.AnyHttpUrl
