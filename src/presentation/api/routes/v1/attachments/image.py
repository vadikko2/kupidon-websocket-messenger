import typing

import cqrs
import fastapi
import pydantic
from fastapi_app import response
from fastapi_app.exception_handlers import registry

from domain import exceptions as domain_exceptions
from presentation.api import dependencies
from presentation.api.schema.v1 import responses
from service import exceptions as service_exceptions
from service.requests.attachments import upload_image as upload_image_requests

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
    image_height: pydantic.NonNegativeInt = fastapi.Body(description="Image height"),
    image_width: pydantic.NonNegativeInt = fastapi.Body(description="Image width"),
    request_mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> response.Response[responses.Uploaded[responses.ImageInfo]]:
    """
    # Uploads image
    """
    result: upload_image_requests.ImageUploaded = await request_mediator.send(
        upload_image_requests.UploadImage(
            chat_id=chat_id,
            uploader=account_id,
            height=image_height,
            width=image_width,
            content=image_file.file.read(),
        ),
    )
    return response.Response[responses.Uploaded[responses.ImageInfo]](
        result=responses.Uploaded[responses.ImageInfo](
            attachment_id=result.attachment_id,
            info=responses.ImageInfo(
                download_url=result.attachment_urls[0],  # pyright: ignore[reportArgumentType]
                height=image_height,
                width=image_width,
                url_100x100=result.attachment_urls[1],  # pyright: ignore[reportArgumentType]
                url_200x200=result.attachment_urls[2],  # pyright: ignore[reportArgumentType]
            ),
        ),
    )
