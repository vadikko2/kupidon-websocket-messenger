import typing

import cqrs
import fastapi
import pydantic
from fastapi_app.exception_handlers import registry

from domain import exceptions as domain_exceptions
from domain.attachments import image
from presentation.api import dependencies
from service import exceptions as service_exceptions

router = fastapi.APIRouter(prefix="")


@router.post(
    "",
    status_code=fastapi.status.HTTP_201_CREATED,
    responses=registry.get_exception_responses(
        service_exceptions.ChatNotFound,
        service_exceptions.AttachmentUploadError,
        domain_exceptions.AttachmentAlreadyUploaded,
    ),
)
async def upload_image(
    chat_id: pydantic.UUID4,
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    image_file: fastapi.UploadFile = fastapi.File(description="Image file"),
    image_type: image.ImageTypes = fastapi.Body(description="Image type", default=image.ImageTypes.JPEG),
    image_height: pydantic.NonNegativeInt = fastapi.Body(description="Image height"),
    image_width: pydantic.NonNegativeInt = fastapi.Body(description="Image width"),
    request_mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
):
    """
    # Uploads image
    """
    pass
