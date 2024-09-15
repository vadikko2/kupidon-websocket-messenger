import typing
import uuid


class AlreadyChatParticipant(Exception):
    def __init__(self, account_id: typing.Text, chat_id: uuid.UUID) -> None:
        super().__init__(f"Account {account_id} already is chat {chat_id} participant")


class DuplicateMessage(Exception):
    def __init__(self, message_id: uuid.UUID, chat_id: uuid.UUID) -> None:
        super().__init__(f"Message {message_id} in chat {chat_id} already exists")


class TooManyReactions(Exception):
    def __init__(
        self,
        reactor: typing.Text,
        reaction_id: uuid.UUID,
        message_id: uuid.UUID,
    ) -> None:
        super().__init__(
            f"Too many reactions on message {message_id} to react by {reactor} with reaction {reaction_id}",
        )
