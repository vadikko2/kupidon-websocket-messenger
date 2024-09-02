import functools

import fastapi

from presentation.api.schema import constants

_MessageValidationParams = dict(
    description="Message content",
    examples=["Hello World!"],
    min_length=constants.MIN_MESSAGE_LENGTH,
    max_length=constants.MAX_MESSAGE_LENGTH,
    json_schema_extra={"nullable": False},
    frozen=True,
)
MessageBody = functools.partial(
    fastapi.Body,
    **_MessageValidationParams,
)
