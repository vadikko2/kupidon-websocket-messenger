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
        raise exceptions.ParticipantNotInChat(sender, requested_chat)


def raise_if_first_writer_required_and_sender_not_allowed(
    loaded_chat: chats.Chat,
    requested_chat: uuid.UUID,
    sender: str,
) -> None:
    """
    If any participant in the chat has first_writer=True and the chat has no messages yet,
    only participants with first_writer=True can send the first message.
    """
    if loaded_chat.last_message is not None:
        return
    if not any(p.first_writer for p in loaded_chat.participants):
        return
    participant = loaded_chat.is_participant(sender)
    if participant is None or not participant.first_writer:
        raise exceptions.FirstWriterRequired(requested_chat, sender)
