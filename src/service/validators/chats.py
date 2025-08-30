import uuid

from domain import chats
from service import exceptions


def raise_if_sender_not_in_chat(
    loaded_chat: chats.Chat,
    requested_chat: uuid.UUID,
    sender: str,
) -> None:
    # Check participants
    if not loaded_chat.is_participant(sender):
        raise exceptions.ParticipantNotInChat(
            sender,
            requested_chat,
        )
