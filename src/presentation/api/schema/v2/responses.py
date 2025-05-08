import typing

import pydantic


class VoiceUploaded(pydantic.BaseModel, frozen=True):
    attachment_id: pydantic.UUID4


class VoiceInfo(pydantic.BaseModel, frozen=True):
    download_url: pydantic.AnyHttpUrl = pydantic.Field(description="Download URL")
    amplitudes: typing.List[pydantic.NonNegativeFloat] | None = pydantic.Field(description="Amplitudes", default=None)
    amplitudes_count: pydantic.NonNegativeInt | None = pydantic.Field(description="Amplitudes count", default=None)


class Voices(pydantic.BaseModel, frozen=True):
    voices: typing.List[VoiceInfo] = pydantic.Field(description="Voices", default_factory=list)
