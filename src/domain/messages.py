import datetime
import logging
import typing
import uuid

import cqrs
import pydantic

from domain import (
    attachments as attachment_entities,
    events,
    exceptions,
    reactions as reaction_entities,
)

logger = logging.getLogger(__name__)

TOTAL_EMOJI_NUMBER = 12
EMOJI_PER_REACTOR = 3


class Message(pydantic.BaseModel):
    """
    Message entity
    """

    chat_id: pydantic.UUID4 = pydantic.Field(frozen=True)
    message_id: pydantic.UUID4 = pydantic.Field(default_factory=uuid.uuid4, frozen=True)
    sender: typing.Text = pydantic.Field(frozen=True)
    reply_to: typing.Optional[pydantic.UUID4] = pydantic.Field(default=None, frozen=True)
    deleted: bool = False

    content: typing.Optional[typing.Text] = pydantic.Field(frozen=True, default=None)
    attachments: typing.List[attachment_entities.Attachment] = pydantic.Field(
        default_factory=list,
        max_length=5,
        frozen=True,
    )
    reactions: typing.List[reaction_entities.Reaction] = pydantic.Field(
        default_factory=list,
        max_length=TOTAL_EMOJI_NUMBER,
    )

    created: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now,
        frozen=True,
    )
    updated: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now,
    )

    event_list: typing.List[cqrs.DomainEvent] = pydantic.Field(
        default_factory=list,
        exclude=True,
    )

    def delete(self) -> None:
        if self.deleted:
            logger.debug(f"Message {self.message_id} already deleted")
            return

        self.deleted = True
        self.updated = datetime.datetime.now()
        logger.debug(f"Message {self.message_id} deleted")
        self.event_list.append(
            events.MessageDeleted(
                chat_id=self.chat_id,
                message_id=self.message_id,
                message_sender=self.sender,
            ),
        )

    def _get_reactions_per_reactor(self, reactor: typing.Text) -> int:
        """
        Returns number of reactions per reactor
        """
        return len(
            [reaction for reaction in self.reactions if reaction.reactor == reactor],
        )

    def _already_reacted_by_reactor(
        self,
        emoji: typing.Text,
        reactor: typing.Text,
    ) -> bool:
        """
        Returns True if reactor already reacted with emoji
        """
        return bool(
            [reaction for reaction in self.reactions if reaction.reactor == reactor and reaction.emoji == emoji],
        )

    def react(self, reaction: reaction_entities.Reaction) -> None:
        """
        Reacts to message
        """
        if self._already_reacted_by_reactor(reaction.emoji, reaction.reactor):
            logger.debug(
                f"Message {self.message_id} already reacted by {reaction.reactor} with {reaction.emoji}",
            )
            return

        if len(self.reactions) == TOTAL_EMOJI_NUMBER:
            raise exceptions.TooManyReactions(
                reactor=reaction.reactor,
                reaction_id=reaction.reaction_id,
                message_id=self.message_id,
            )

        if self._get_reactions_per_reactor(reaction.reactor) == EMOJI_PER_REACTOR:
            raise exceptions.TooManyReactions(
                reactor=reaction.reactor,
                reaction_id=reaction.reaction_id,
                message_id=self.message_id,
            )

        self.reactions.append(reaction)
        logger.debug(
            f"Message {self.message_id} reacted by {reaction.reactor} with {reaction.emoji}",
        )
        self.event_list.append(
            events.MessageReacted(
                reaction_id=reaction.reaction_id,
                reactor=reaction.reactor,
                message_id=self.message_id,
                emoji=reaction.emoji,
            ),
        )

    def unreact(self, reaction: reaction_entities.Reaction) -> None:
        """
        Unreacts from message
        """
        len_before_remove = len(self.reactions)
        self.reactions.remove(reaction)

        if len(self.reactions) == len_before_remove:
            return

        logger.debug(
            f"Message {self.message_id} unreacted by {reaction.reactor} with {reaction.emoji}",
        )
        self.event_list.append(
            events.MessageUnreacted(
                reaction_id=reaction.reaction_id,
                message_id=self.message_id,
            ),
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

    def __eq__(self, other):
        if not isinstance(other, Message):
            return False
        return self.message_id == other.message_id

    def __repr__(self):
        return f"Message({self.message_id}, {self.chat_id}, {self.content}, {self.created})"


class ReedMessage(pydantic.BaseModel):
    """
    Represents a message that has been reed by an actor
    """

    actor: typing.Text
    message: Message
    timestamp: datetime.datetime = pydantic.Field(default_factory=datetime.datetime.now)

    def __hash__(self):
        return hash(self.message.message_id)

    def __eq__(self, other):
        if not isinstance(other, ReedMessage):
            return False
        return self.message.message_id == other.message.message_id
