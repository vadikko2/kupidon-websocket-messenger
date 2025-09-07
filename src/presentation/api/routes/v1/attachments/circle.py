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
from service.models.attachments import upload_circle as upload_circle_request

router = fastapi.APIRouter(prefix="")


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses=registry.get_exception_responses(
        service_exceptions.ChatNotFound,
        service_exceptions.AttachmentUploadError,
        domain_exceptions.AttachmentAlreadyUploaded,
        service_exceptions.UnsupportedVoiceFormat,
        service_exceptions.GetUserIdError,
        service_exceptions.UnauthorizedError,
    ),
)
async def upload_circle(
    chat_id: pydantic.UUID4,
    account_id: str = fastapi.Depends(security.extract_account_id),
    circle_file: fastapi.UploadFile = fastapi.File(description="Circle file"),
    circle_type: attachments.CircleTypes = fastapi.Body(
        description="Circle type",
        default=attachments.CircleTypes.MP4,
    ),
    duration_milliseconds: pydantic.PositiveInt = fastapi.Body(description="Circle duration in milliseconds"),
    request_mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> response.Response[responses.Uploaded[responses.CircleInfo]]:
    """
    # Uploads circle
    """
    result: upload_circle_request.CircleUploaded = await request_mediator.send(
        upload_circle_request.UploadCircle(
            chat_id=chat_id,
            uploader=account_id,
            circle_format=circle_type,
            duration_milliseconds=duration_milliseconds,
            content=circle_file.file.read(),
        ),
    )
    return response.Response[responses.Uploaded[responses.CircleInfo]](
        result=responses.Uploaded[responses.CircleInfo](
            attachment_id=result.attachment_id,
            info=responses.CircleInfo(
                duration_milliseconds=duration_milliseconds,
                download_url=result.attachment_url,  # pyright: ignore[reportArgumentType]
                circle_type=circle_type,
            ),
        ),
    )
