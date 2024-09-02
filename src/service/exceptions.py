import typing
import uuid

from domain import message


class ChangeStatusAccessDonated(Exception):

    def __init__(self, actor: typing.Text, message_id: uuid.UUID, new_status: message.MessageStatus) -> None:
        super().__init__(f"Failed to change status to {new_status} for message {message_id}: {actor}")
