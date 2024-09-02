import typing
import uuid

from domain import message


class ChangeStatusAccessDonated(Exception):
    def __init__(
        self,
        actor: typing.Text,
        message_id: uuid.UUID,
        new_status: message.MessageStatus,
    ) -> None:
        super().__init__(
            f"Failed to change status to {new_status} for message {message_id}: {actor}",
        )


class MessageNotFound(Exception):
    def __init__(self, message_id: uuid.UUID) -> None:
        super().__init__(f"Message {message_id} not found")


class StartSubscriptionError(Exception):
    def __init__(self, account_id: typing.Text, exception: Exception) -> None:
        super().__init__(
            f"Failed to start subscription for account {account_id}: {exception}",
        )
