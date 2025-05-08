import typing

import pydantic

MAX_GET_VOICES_LIMIT = 10


class GetVoices(pydantic.BaseModel, frozen=True):
    attachments: typing.List[pydantic.UUID4] = pydantic.Field(
        description="Attachments IDs",
        default_factory=list,
        max_length=MAX_GET_VOICES_LIMIT,
    )
