import datetime
import typing

import pydantic

from domain import attachments


class MessageSent(pydantic.BaseModel):
    message_id: pydantic.UUID4
    timestamp: datetime.datetime


class ChatCreated(pydantic.BaseModel):
    chat_id: pydantic.UUID4


Info = typing.TypeVar("Info", bound=pydantic.BaseModel)


class Uploaded(pydantic.BaseModel, typing.Generic[Info], frozen=True):
    attachment_id: pydantic.UUID4

    info: Info


class VoiceInfo(pydantic.BaseModel, frozen=True):
    download_url: pydantic.AnyHttpUrl = pydantic.Field(description="Download URL")

    voice_type: attachments.VoiceTypes = pydantic.Field(description="Voice type")
    duration_milliseconds: pydantic.PositiveInt = pydantic.Field(description="Voice length in milliseconds")

    amplitudes: typing.List[typing.Tuple[pydantic.StrictInt, pydantic.StrictInt]] = pydantic.Field(
        description="Voice amplitude",
        default_factory=list,
    )

    @pydantic.computed_field(return_type=int)
    @property
    def amplitudes_count(self) -> int:
        return len(self.amplitudes) if self.amplitudes is not None else 0


class ImageInfo(pydantic.BaseModel, frozen=True):
    download_url: pydantic.AnyHttpUrl = pydantic.Field(description="Download URL")

    url_100x100: pydantic.AnyHttpUrl
    url_200x200: pydantic.AnyHttpUrl

    height: pydantic.NonNegativeInt = pydantic.Field(description="Image height")
    width: pydantic.NonNegativeInt = pydantic.Field(description="Image width")
