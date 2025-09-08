import uuid


class ParticipantNotInChat(Exception):
    def __init__(self, account_id: str, chat_id: uuid.UUID) -> None:
        super().__init__(
            f"Account {account_id} is not a participant in chat {chat_id}",
        )


class MessageNotFound(Exception):
    def __init__(self, message_id: uuid.UUID) -> None:
        super().__init__(f"Message {message_id} not found")


class ChatNotFound(Exception):
    def __init__(self, chat_id: uuid.UUID) -> None:
        super().__init__(f"Chat {chat_id} not found")


class AttachmentNotFound(Exception):
    def __init__(self, attachment_id: uuid.UUID) -> None:
        super().__init__(f"Attachment {attachment_id} not found")


class AttachmentNotForChat(Exception):
    def __init__(self, attachment_id: uuid.UUID, chat_id: uuid.UUID) -> None:
        super().__init__(f"Attachment {attachment_id} not for chat {chat_id}")


class AttachmentNotForSender(Exception):
    def __init__(self, attachment_id: uuid.UUID, account_id: str) -> None:
        super().__init__(f"Attachment {attachment_id} not for account {account_id}")


class AttachmentUploadError(Exception):
    def __init__(self, exception: Exception) -> None:
        super().__init__(
            f"Failed to upload attachment: {exception}",
        )


class StartSubscriptionError(Exception):
    def __init__(self, account_id: str, exception: Exception) -> None:
        super().__init__(
            f"Failed to start subscription for account {account_id}: {exception}",
        )


class SubscriptionNotStarted(Exception):
    def __init__(self) -> None:
        super().__init__("Subscription not started")


class MessageNotDeleted(Exception):
    def __init__(self, message_id: uuid.UUID) -> None:
        super().__init__(f"Message {message_id} not deleted")


class UnsupportedVoiceFormat(Exception):
    def __init__(self, format_name: str) -> None:
        super().__init__(f"Unsupported voice format: {format_name}")


class MessageNotForAccount(Exception):
    def __init__(self, message_id: uuid.UUID, account_id: str) -> None:
        super().__init__(
            f"Message {message_id} not for account {account_id}",
        )


class GetUserIdError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


class FirstWriterRequired(Exception):
    def __init__(self, chat_id: uuid.UUID, account_id: str) -> None:
        super().__init__(
            f"Account {account_id} is not allowed to write first in chat {chat_id}",
        )
