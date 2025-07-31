from domain import messages
from service import exceptions


def raise_if_message_deleted(loaded_message: messages.Message) -> None:
    if loaded_message.deleted:
        raise exceptions.MessageNotFound(loaded_message.message_id)


def raise_if_message_not_deleted(loaded_message: messages.Message) -> None:
    if not loaded_message.deleted:
        raise exceptions.MessageNotDeleted(loaded_message.message_id)
