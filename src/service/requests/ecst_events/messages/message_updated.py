import typing

import pydantic

from domain.attachments import attachments


class MessageUpdatedPayload(pydantic.BaseModel):
    chat_id: pydantic.UUID4
    message_id: pydantic.UUID4
    message_sender: typing.Text
    message_content: typing.Optional[typing.Text]

    message_attachments: typing.List[attachments.Attachment]
