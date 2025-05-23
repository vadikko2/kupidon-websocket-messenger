import typing
import uuid


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
