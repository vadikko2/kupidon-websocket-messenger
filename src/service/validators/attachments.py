import typing
import uuid

from domain import attachments
from service import exceptions


def raise_if_attachment_not_found(
    loaded_attachments: typing.Sequence[attachments.Attachment],
    request_attachments: typing.Sequence[uuid.UUID],
):
    """
    Validates that all attachments are present in the database and that they are
    valid for the chat and sender
    """
    difference = set(request_attachments) - set(
        [att.attachment_id for att in loaded_attachments],
    )

    if difference:
        raise exceptions.AttachmentNotFound(next(iter(difference)))


def raise_if_attachment_not_for_chat(
    loaded_attachments: typing.Sequence[attachments.Attachment],
    chat_id: uuid.UUID,
):
    not_for_chat_attach = next(filter(lambda a: a.chat_id != chat_id, loaded_attachments), None)
    if not_for_chat_attach:
        raise exceptions.AttachmentNotForChat(not_for_chat_attach.attachment_id, chat_id)


def raise_if_attachment_not_for_sender(
    loaded_attachments: typing.Sequence[attachments.Attachment],
    uploader: typing.Text,
):
    not_for_sender_attach = next(filter(lambda a: a.uploader != uploader, loaded_attachments), None)
    if not_for_sender_attach:
        raise exceptions.AttachmentNotForSender(not_for_sender_attach.attachment_id, uploader)
