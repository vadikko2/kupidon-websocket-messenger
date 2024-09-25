import datetime
import logging
import typing
import uuid

import cqrs
import pydantic

from domain import events, exceptions, messages

logger = logging.getLogger(__name__)


class Chat(pydantic.BaseModel):
    """
    Chat entity
    """

    chat_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4, frozen=True)
    name: typing.Text | None = pydantic.Field(default=None, max_length=100)

    created: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)
    updated: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    initiator: typing.Text = pydantic.Field(
        description="Initiator account ID",
        frozen=True,
    )
    participants: typing.List[typing.Text] = pydantic.Field(default_factory=list)

    last_message: typing.Optional[uuid.UUID] = None
    last_activity_timestamp: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now,
    )

    history: typing.List[messages.Message] = pydantic.Field(default_factory=list)

    deleted: bool = False

    event_list: typing.List[cqrs.DomainEvent] = pydantic.Field(default_factory=list)

    @pydantic.computed_field()
    def participants_count(self) -> pydantic.NonNegativeInt:
        return len(self.participants)

    def add_message(self, message: messages.Message) -> None:
        """
        Registers new message
        """
        if message in self.history:
            raise exceptions.DuplicateMessage(message.message_id, self.chat_id)

        self.history.append(message)

        self.last_message = message.message_id
        self.last_activity_timestamp = message.created

        logger.debug(f"Message {message.message_id} added to chat {self.chat_id}")

        self.event_list.append(
            events.NewMessageAdded(
                chat_id=self.chat_id,
                message_id=message.message_id,
            ),
        )

    def add_participant(
        self,
        account_id: typing.Text,
        initiated_by: typing.Text,
    ) -> None:
        """
        Adds new participant to chat
        """
        if account_id in self.participants:
            raise exceptions.AlreadyChatParticipant(account_id, self.chat_id)

        self.participants.append(account_id)

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

    def is_participant(self, account_id: typing.Text) -> bool:
        """
        Checks if account is participant
        """
        return account_id in self.participants

    def get_events(self) -> typing.List[cqrs.DomainEvent]:
        """
        Returns new domain events
        """
        new_events = []
        while self.event_list:
            new_events.append(self.event_list.pop())
        return new_events

    def __hash__(self):
        return hash(self.chat_id)
