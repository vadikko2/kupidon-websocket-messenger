import datetime
import logging
import typing
import uuid

import cqrs
import pydantic

from domain import events, messages

logger = logging.getLogger(__name__)


class Participant(pydantic.BaseModel):
    """
    Participant entity
    """

    account_id: typing.Text = pydantic.Field(frozen=True)
    initiated_by: typing.Text = pydantic.Field(frozen=True)

    last_read_message: typing.Optional[messages.Message] = pydantic.Field(default=None)

    def set_last_read_message(self, message: messages.Message):
        self.last_read_message = message

    def __eq__(self, other):
        if not isinstance(other, Participant):
            return False
        return self.account_id == other.account_id

    def __hash__(self):
        return hash(self.account_id)

    def __repr__(self):
        return self.account_id

    def __str__(self):
        return self.account_id


class Chat(pydantic.BaseModel):
    """
    Chat entity
    """

    chat_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4, frozen=True)
    name: typing.Text = pydantic.Field(min_length=1, max_length=100)
    avatar: pydantic.AnyHttpUrl | None = pydantic.Field(default=None)

    created: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now,
        frozen=True,
    )

    initiator: typing.Text = pydantic.Field(
        description="Initiator account ID",
        frozen=True,
    )
    participants: typing.Set[Participant] = pydantic.Field(default_factory=set)

    last_message: typing.Optional[messages.Message] = pydantic.Field(default=None)
    last_activity_timestamp: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now,
    )

    history: typing.List[messages.Message] = pydantic.Field(default_factory=list)

    event_list: typing.List[cqrs.DomainEvent] = pydantic.Field(
        default_factory=list,
        exclude=True,
    )

    @pydantic.computed_field()
    @property
    def participants_count(self) -> pydantic.NonNegativeInt:
        return len(self.participants)

    @pydantic.computed_field()
    @property
    def last_message_id(self) -> typing.Optional[uuid.UUID]:
        if self.last_message is None:
            return None
        return self.last_message.message_id

    def add_message(self, message: messages.Message) -> None:
        """
        Registers new message
        """
        if message in self.history:
            return

        self.history.append(message)

        self.last_message = (
            max((message, self.last_message), key=lambda x: x.created)
            if self.last_message
            else message
        )
        self.last_activity_timestamp = message.created

        logger.debug(f"Message {message.message_id} added to chat {self.chat_id}")

        self.event_list.append(
            events.NewMessageAdded(
                chat_id=self.chat_id,
                message_id=message.message_id,
            ),
        )

    def read_message(
        self,
        reader: typing.Text,
        message: messages.Message,
    ) -> messages.ReedMessage | None:
        if message.deleted:
            return

        if (participant := self.is_participant(reader)) is None:
            return

        participant.set_last_read_message(message)

        logger.debug(f"Message {message.message_id} read by {reader}")
        read_message = messages.ReedMessage(actor=reader, message=message)
        events.MessageRead(
            chat_id=message.chat_id,
            message_id=message.message_id,
            reader_id=reader,
            read_at=read_message.timestamp,
        )
        return read_message

    def add_participant(
        self,
        account_id: typing.Text,
        initiated_by: typing.Text,
    ) -> None:
        """
        Adds new participant to chat
        """
        if self.is_participant(account_id):
            return

        self.participants.add(
            Participant(account_id=account_id, initiated_by=initiated_by),
        )
        logger.debug(
            f"Account {account_id} added to chat {self.chat_id} by {initiated_by}",
        )

        self.event_list.append(
            events.NewParticipantAdded(
                chat_id=self.chat_id,
                account_id=account_id,
                invited_by=initiated_by,
            ),
        )

    def delete_for(self, account_id: typing.Text) -> None:
        """
        Deletes chat for specified account
        """
        if (participant := self.is_participant(account_id)) is None:
            return

        self.participants.remove(participant)

        logger.debug(f"Chat {self.chat_id} deleted for {account_id}")

    def last_read_by(self, account_id: typing.Text) -> messages.Message | None:
        if (participant := self.is_participant(account_id)) is None:
            return

        return participant.last_read_message

    def is_participant(self, account_id: typing.Text) -> Participant | None:
        """
        Checks if account is participant
        """
        return next((p for p in self.participants if p.account_id == account_id), None)

    def get_events(self) -> typing.List[cqrs.DomainEvent]:
        """
        Returns new domain events
        """
        new_events = []
        while self.event_list:
            new_events.append(self.event_list.pop())
        return new_events

    def __eq__(self, other):
        if not isinstance(other, Chat):
            return False
        return self.chat_id == other.chat_id

    def __hash__(self):
        return hash(self.chat_id)
