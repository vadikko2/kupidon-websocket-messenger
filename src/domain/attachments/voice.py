import enum

import pydantic


class VoiceTypes(enum.StrEnum):
    MP3 = "mp3"
    WAV = "wav"


class VoiceAttachmentMeta(pydantic.BaseModel):
    voice_type: VoiceTypes = pydantic.Field(description="Voice type")
    duration_seconds: pydantic.PositiveInt = pydantic.Field(description="Voice duration in seconds")
    duration_milliseconds: pydantic.PositiveInt = pydantic.Field(description="Voice duration in duration_milliseconds")

    amplitudes: list[tuple[pydantic.StrictInt, pydantic.StrictInt]] | None = pydantic.Field(
        description="Voice amplitude",
        default=None,
    )

    @pydantic.model_validator(mode="after")
    def check_content(self):
        self.duration_seconds = self.duration_milliseconds // 1000
        return self
