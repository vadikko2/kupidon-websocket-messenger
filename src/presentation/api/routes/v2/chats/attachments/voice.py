import logging
import typing

import cqrs
import fastapi
import pydantic
from fastapi_app import response
from fastapi_app.exception_handlers import registry
from starlette import status

from presentation.api import dependencies
from presentation.api.schema.v2 import requests, responses
from service import exceptions

router = fastapi.APIRouter(prefix="/voice", tags=["Attachments"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses=registry.get_exception_responses(exceptions.ChatNotFound),
)
def upload_voice(
    chat_id: pydantic.UUID4,
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    voice_file: fastapi.UploadFile = fastapi.File(description="Voice file"),
    voice_type: typing.Literal["wav", "mp3"] = fastapi.Body(description="Voice type", default="mp3"),
    request_mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> response.Response[responses.VoiceUploaded]:
    import uuid

    return response.Response[responses.VoiceUploaded](result=responses.VoiceUploaded(attachment_id=uuid.uuid4()))


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses=registry.get_exception_responses(exceptions.ChatNotFound),
)
def get_voice(
    chat_id: pydantic.UUID4,
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    body: requests.GetVoices = fastapi.Body(...),
    request_mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> response.Response[responses.Voices]:
    return response.Response[responses.Voices](result=responses.Voices(voices=[]))
