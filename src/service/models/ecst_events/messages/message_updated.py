import pydantic

from domain.attachments import attachments


class MessageUpdatedPayload(pydantic.BaseModel):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4
    message_sender: str
    message_content: str | None

    message_attachments: list[attachments.Attachment]
