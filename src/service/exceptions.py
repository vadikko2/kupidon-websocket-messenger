import typing
import uuid

from domain import messages


class ChangeStatusAccessDonated(Exception):
    def __init__(
        self,
        actor: typing.Text,
        message_id: uuid.UUID,
        new_status: messages.MessageStatus,
    ) -> None:
        super().__init__(
            f"Failed to change status to {new_status} for message {message_id}: {actor}",
        )


class ParticipantNotInChat(Exception):
    def __init__(self, account_id: typing.Text, chat_id: uuid.UUID) -> None:
        super().__init__(
            f"Account {account_id} is not a participant in chat {chat_id}",
        )


class MessageNotFound(Exception):
    def __init__(self, message_id: uuid.UUID) -> None:
        super().__init__(f"Message {message_id} not found")


class ChatNotFound(Exception):
    def __init__(self, chat_id: uuid.UUID) -> None:
        super().__init__(f"Chat {chat_id} not found")


class StartSubscriptionError(Exception):
    def __init__(self, account_id: typing.Text, exception: Exception) -> None:
        super().__init__(
            f"Failed to start subscription for account {account_id}: {exception}",
        )


class SubscriptionNotStarted(Exception):
    def __init__(self) -> None:
        super().__init__("Subscription not started")
