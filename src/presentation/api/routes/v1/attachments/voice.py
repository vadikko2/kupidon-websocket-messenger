import cqrs
import fastapi
import pydantic
from fastapi_app import response
from fastapi_app.exception_handlers import registry
from starlette import status

from domain import attachments, exceptions as domain_exceptions
from presentation.api import dependencies, security
from presentation.api.schema.v1 import responses
from service import exceptions as service_exceptions
from service.models.attachments import upload_voice as upload_voice_request

router = fastapi.APIRouter(prefix="")


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses=registry.get_exception_responses(
        service_exceptions.ChatNotFound,
        service_exceptions.AttachmentUploadError,
        service_exceptions.UnsupportedVoiceFormat,
        service_exceptions.GetUserIdError,
        service_exceptions.UnauthorizedError,
        domain_exceptions.AttachmentAlreadyUploaded,
    ),
)
async def upload_voice(
    chat_id: pydantic.UUID4,
    account_id: str = fastapi.Depends(security.extract_account_id),
    voice_file: fastapi.UploadFile = fastapi.File(description="Voice file"),
    voice_type: attachments.VoiceTypes = fastapi.Body(description="Voice type", default=attachments.VoiceTypes.MP3),
    duration_milliseconds: pydantic.PositiveInt = fastapi.Body(description="Voice duration in milliseconds"),
    request_mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> response.Response[responses.Uploaded[responses.VoiceInfo]]:
    """
    # Uploads voice
    """
    result: upload_voice_request.VoiceUploaded = await request_mediator.send(
        upload_voice_request.UploadVoice(
            chat_id=chat_id,
            uploader=account_id,
            voice_format=voice_type,
            duration_milliseconds=duration_milliseconds,
            content=voice_file.file.read(),
        ),
    )
    return response.Response[responses.Uploaded[responses.VoiceInfo]](
        result=responses.Uploaded[responses.VoiceInfo](
            attachment_id=result.attachment_id,
            info=responses.VoiceInfo(
                duration_milliseconds=duration_milliseconds,
                download_url=result.attachment_url,  # pyright: ignore[reportArgumentType]
                voice_type=voice_type,
                amplitudes=result.amplitudes,
            ),
        ),
    )
