import enum

import pydantic


class CircleTypes(enum.StrEnum):
    MP4 = "mp4"


class CircleAttachmentMeta(pydantic.BaseModel):
    circle_type: CircleTypes = pydantic.Field(description="Circle type")
    duration_seconds: pydantic.PositiveInt = pydantic.Field(description="Circle duration in seconds")
    duration_milliseconds: pydantic.PositiveInt = pydantic.Field(description="Circle duration in duration_milliseconds")

    @pydantic.model_validator(mode="after")
    def check_content(self):
        self.duration_seconds = self.duration_milliseconds // 1000
        return self
