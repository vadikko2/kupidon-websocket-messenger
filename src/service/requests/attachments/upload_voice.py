import typing

import cqrs
import pydantic

from domain import attachments


class UploadVoice(cqrs.Request):
    chat_id: pydantic.UUID4
    uploader: typing.Text

    voice_format: attachments.VoiceTypes

    content: bytes = pydantic.Field(exclude=True)
    duration_milliseconds: pydantic.NonNegativeInt


class VoiceUploaded(cqrs.Response):
    attachment_id: pydantic.UUID4
    attachment_url: typing.Text

    amplitudes: typing.List[typing.Tuple[pydantic.StrictInt, pydantic.StrictInt]]
