import uuid


class TooManyReactions(Exception):
    def __init__(
        self,
        reactor: str,
        reaction_id: uuid.UUID,
        message_id: uuid.UUID,
    ) -> None:
        super().__init__(
            f"Too many reactions on message {message_id} to react by {reactor} with reaction {reaction_id}",
        )


class AttachmentAlreadyUploaded(Exception):
    def __init__(self, attachment_id: uuid.UUID) -> None:
        super().__init__(f"Attachment {attachment_id} already uploaded")


class AttachmentAlreadySent(Exception):
    def __init__(self, attachment_id: uuid.UUID) -> None:
        super().__init__(f"Attachment {attachment_id} already sent")


class ParticipantNotInChat(Exception):
    def __init__(self, account_id: str, chat_id: uuid.UUID) -> None:
        super().__init__(f"Participant {account_id} not in chat {chat_id}")
