import typing

import cqrs
import pydantic

from domain.attachments import voice


class UploadVoice(cqrs.Request):
    chat_id: pydantic.UUID4
    uploader: typing.Text

    voice_format: voice.VoiceTypes

    content: bytes = pydantic.Field(exclude=True)
    duration_seconds: pydantic.NonNegativeInt


class VoiceUploaded(cqrs.Response):
    attachment_id: pydantic.UUID4
    attachment_url: typing.Text

    amplitudes: typing.List[pydantic.StrictInt]
