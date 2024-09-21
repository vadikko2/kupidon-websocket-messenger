import logging
import typing
import uuid

import cqrs
import fastapi
import pydantic
from fastapi_app import response
from fastapi_app.exception_handlers import registry
from starlette import status

from domain import attachments as attachment_entities
from presentation import dependencies
from presentation.api.schema import responses
from service import exceptions
from service.requests import (
    get_attachments as get_attachments_request,
    upload_attachment as upload_attachment_request,
)
from service.services import upload_attachment as upload_attachment_service

router = fastapi.APIRouter(prefix="/{chat_id}/attachments")

logger = logging.getLogger(__name__)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses=registry.get_exception_responses(exceptions.ChatNotFound),
)
async def upload_attachment(
    chat_id: uuid.UUID,
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    attachment: fastapi.UploadFile = fastapi.File(...),
    content_type: attachment_entities.AttachmentType = fastapi.Body(...),
    upload_attachment_handler: upload_attachment_service.UploadAttachmentService = fastapi.Depends(
        dependency=dependencies.upload_attachment_service_factory,
    ),
    emitter: cqrs.EventEmitter = fastapi.Depends(
        dependency=dependencies.event_emitter_factory,
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

    logger.debug(f"Uploading attachment: {attachment.filename}")
    result = await upload_attachment_handler.handle(
        chat_id=chat_id,
        uploader=account_id,
        file_object=attachment.file,
        filename=attachment.filename,
        content_type=content_type,
    )
    for event in upload_attachment_handler.events():
        try:
            await emitter.emit(event)
        except Exception as emit_error:
            logger.error(f"Failed to emit event {event}: {emit_error}")
    return response.Response(result=result)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses=registry.get_exception_responses(
        exceptions.ChatNotFound,
    ),
)
async def get_attachments(
    chat_id: uuid.UUID,
    limit: pydantic.NonNegativeInt = fastapi.Query(default=10),
    offset: pydantic.NonNegativeInt = fastapi.Query(default=0),
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> response.Response[responses.AttachmentsPage]:
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
        result=responses.AttachmentsPage(
            chat_id=result.chat_id,
            attachments=result.attachments,
            limit=limit,
            offset=offset,
        ),
    )
