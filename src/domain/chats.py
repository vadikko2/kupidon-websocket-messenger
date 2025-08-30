import datetime
import logging
import uuid

import cqrs
import pydantic

from domain import events, exceptions, messages, participants as participant_entities

logger = logging.getLogger(__name__)


class Chat(pydantic.BaseModel):
    """
    Chat entity
    """

    chat_id: pydantic.UUID4 = pydantic.Field(default_factory=uuid.uuid4, frozen=True)
    name: str = pydantic.Field(min_length=1, max_length=100)
    avatar: str | None = pydantic.Field(default=None)

    created: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now,
        frozen=True,
    )

    initiator: str = pydantic.Field(
        description="Initiator account ID",
        frozen=True,
    )
    participants: set[participant_entities.Participant] = pydantic.Field(default_factory=set)

    last_message: messages.Message | None = pydantic.Field(default=None)
    last_activity_timestamp: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now,
    )

    history: list[messages.Message] = pydantic.Field(
        default_factory=list,
        exclude=True,
    )

    event_list: list[cqrs.DomainEvent] = pydantic.Field(
        default_factory=list,
        exclude=True,
    )

    @pydantic.computed_field()
    @property
    def participants_count(self) -> int:
        return len(self.participants)

    @pydantic.computed_field()
    @property
    def last_message_id(self) -> uuid.UUID | None:
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

        self.last_message = max((message, self.last_message), key=lambda x: x.created) if self.last_message else message
        self.last_activity_timestamp = message.created

        logger.debug(f"Message {message.message_id} added to chat {self.chat_id}")

        for attach in message.attachments:
            attach.send(message.message_id)

        self.event_list.append(
            events.NewMessageAdded(
                chat_id=self.chat_id,
                message_id=message.message_id,
                sender=message.sender,
            ),
        )

    def read_message(self, reader: str, message: messages.Message) -> messages.ReedMessage | None:
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

    def add_participant(self, account_id: str, initiated_by: str) -> None:
        """
        Adds new participant to chat
        """
        if self.is_participant(account_id):
            return

        self.participants.add(
            participant_entities.Participant(account_id=account_id, initiated_by=initiated_by),
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

    def add_tag(self, account_id: str, tag: participant_entities.ChatTag) -> None:
        """
        Adds tag to participant
        """
        if (participant := self.is_participant(account_id)) is None:
            raise exceptions.ParticipantNotInChat(account_id, self.chat_id)
        participant.add_tag(tag)

    def remove_tag(self, account_id: str, tag: participant_entities.ChatTag) -> None:
        """
        Removes tag from participant
        """
        if (participant := self.is_participant(account_id)) is None:
            raise exceptions.ParticipantNotInChat(account_id, self.chat_id)
        participant.remove_tag(tag)

    def delete_for(self, account_id: str) -> None:
        """
        Deletes chat for specified account
        """
        if (participant := self.is_participant(account_id)) is None:
            return

        self.participants.remove(participant)

        logger.debug(f"Chat {self.chat_id} deleted for {account_id}")

    def last_read_by(self, account_id: str) -> messages.Message | None:
        if (participant := self.is_participant(account_id)) is None:
            return

        return participant.last_read_message

    def is_participant(self, account_id: str) -> participant_entities.Participant | None:
        """
        Checks if account is participant
        """
        return next((p for p in self.participants if p.account_id == account_id), None)

    def get_events(self) -> list[cqrs.DomainEvent]:
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
