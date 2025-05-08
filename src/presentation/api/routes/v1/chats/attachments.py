import logging
import typing

import cqrs
import fastapi
import pydantic
from fastapi_app import response
from fastapi_app.exception_handlers import registry
from starlette import status

from domain import attachments as attachment_entities
from presentation.api import dependencies
from presentation.api.schema import pagination
from service import exceptions
from service.requests.attachments import (
    get_attachments as get_attachments_request,
    upload_attachment as upload_attachment_request,
)

router = fastapi.APIRouter(prefix="/{chat_id}/attachments", tags=["Attachments"], deprecated=True)

logger = logging.getLogger(__name__)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses=registry.get_exception_responses(exceptions.ChatNotFound),
)
async def upload_attachment(
    chat_id: pydantic.UUID4,
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    attachment: fastapi.UploadFile = fastapi.File(...),
    content_type: attachment_entities.AttachmentType = fastapi.Body(...),
    request_mediator: cqrs.RequestMediator = fastapi.Depends(
        dependencies.request_mediator_factory,
    ),
) -> response.Response[upload_attachment_request.AttachmentUploaded]:
    """
    # Uploads attachment to chat
    """
    if not attachment.filename:
        raise fastapi.exceptions.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    result: upload_attachment_request.AttachmentUploaded = await request_mediator.send(
        upload_attachment_request.UploadAttachment(
            chat_id=chat_id,
            uploader=account_id,
            filename=attachment.filename,
            content_type=content_type,
            content=attachment.file.read(),
        ),
    )
    return response.Response(result=result)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses=registry.get_exception_responses(
        exceptions.ChatNotFound,
    ),
)
async def get_attachments(
    chat_id: pydantic.UUID4,
    limit: pydantic.NonNegativeInt = fastapi.Query(default=10),
    offset: pydantic.NonNegativeInt = fastapi.Query(default=0),
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> response.Response[pagination.Pagination[get_attachments_request.AttachmentInfo]]:
    """
    # Returns all attachments in chat
    """
    result: get_attachments_request.Attachments = await mediator.send(
        get_attachments_request.GetAttachments(
            chat_id=chat_id,
            account_id=account_id,
            limit=limit,
            offset=offset,
        ),
    )
    return response.Response(
        result=pagination.Pagination[get_attachments_request.AttachmentInfo](
            url=f"/v1/chats/{chat_id}/attachments/?",
            base_items=result.attachments,
            limit=limit,
            offset=offset,
        ),
    )
