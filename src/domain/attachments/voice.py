import enum
import typing

import pydantic


class VoiceTypes(enum.StrEnum):
    MP3 = "mp3"
    WAV = "wav"


class VoiceAttachmentMeta(pydantic.BaseModel):
    length: pydantic.NonNegativeInt = pydantic.Field(description="Voice length in seconds")
    voice_type: VoiceTypes = pydantic.Field(description="Voice type")
    duration_seconds: pydantic.PositiveInt = pydantic.Field(description="Voice duration in seconds")

    amplitudes: typing.Optional[typing.List[pydantic.StrictInt]] = pydantic.Field(
        description="Voice amplitude",
        default=None,
    )
