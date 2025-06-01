import datetime
import typing

import cqrs
import pydantic


class NewMessageAdded(cqrs.DomainEvent, frozen=True):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4


class NewParticipantAdded(cqrs.DomainEvent, frozen=True):
    chat_id: pydantic.UUID4
    account_id: typing.Text
    invited_by: typing.Text


class MessageRead(cqrs.DomainEvent, frozen=True):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4
    reader_id: typing.Text
    read_at: datetime.datetime


class MessageDeleted(cqrs.DomainEvent, frozen=True):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4
    message_sender: typing.Text


class NewAttachmentUploaded(cqrs.DomainEvent, frozen=True):
    attachment_id: pydantic.UUID4
    urls: typing.List[pydantic.AnyHttpUrl]


class AttachmentSent(cqrs.DomainEvent, frozen=True):
    message_id: pydantic.UUID4
    attachment_id: pydantic.UUID4


class MessageReacted(cqrs.DomainEvent, frozen=True):
    reaction_id: pydantic.UUID4
    reactor: typing.Text
    message_id: pydantic.UUID4
    emoji: typing.Text


class MessageUnreacted(cqrs.DomainEvent, frozen=True):
    reaction_id: pydantic.UUID4
    message_id: pydantic.UUID4


class TappingInChat(cqrs.DomainEvent, frozen=True):
    chat_id: pydantic.UUID4
    account_id: typing.Text
