import datetime
import uuid

import pydantic


class Reaction(pydantic.BaseModel, frozen=True):
    reaction_id: pydantic.UUID4 = pydantic.Field(default_factory=uuid.uuid4, frozen=True)
    reactor: str = pydantic.Field(frozen=True)
    message_id: pydantic.UUID4 = pydantic.Field(frozen=True)
    emoji: str = pydantic.Field(frozen=True, max_length=1, min_length=1)

    created: datetime.datetime = pydantic.Field(
        default_factory=datetime.datetime.now,
        frozen=True,
    )
