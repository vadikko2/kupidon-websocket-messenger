import datetime
import typing

import pydantic

from domain.attachments import voice


class MessageSent(pydantic.BaseModel):
    message_id: pydantic.UUID4
    timestamp: datetime.datetime


class ChatCreated(pydantic.BaseModel):
    chat_id: pydantic.UUID4


class VoiceUploaded(pydantic.BaseModel, frozen=True):
    attachment_id: pydantic.UUID4

    info: "VoiceInfo"


class VoiceInfo(pydantic.BaseModel, frozen=True):
    download_url: pydantic.AnyHttpUrl = pydantic.Field(description="Download URL")

    voice_type: voice.VoiceTypes = pydantic.Field(description="Voice type")
    duration_milliseconds: pydantic.PositiveInt = pydantic.Field(description="Voice length in milliseconds")

    amplitudes: typing.List[typing.Tuple[pydantic.StrictInt, pydantic.StrictInt]] = pydantic.Field(
        description="Voice amplitude",
        default_factory=list,
    )

    @pydantic.computed_field()
    @property
    def amplitudes_count(self) -> typing.Optional[pydantic.NonNegativeInt]:
        return len(self.amplitudes) if self.amplitudes is not None else 0
