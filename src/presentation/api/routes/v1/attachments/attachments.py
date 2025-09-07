import logging
import typing

import cqrs
import fastapi
import pydantic
from fastapi_app import response
from fastapi_app.exception_handlers import registry
from starlette import status

from domain import attachments as attachment_entities
from presentation.api import dependencies, security
from presentation.api.schema import pagination
from service import exceptions
from service.models.attachments import (
    get_attachments as get_attachments_request,
)

router = fastapi.APIRouter()

logger = logging.getLogger(__name__)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses=registry.get_exception_responses(
        exceptions.ChatNotFound,
        exceptions.GetUserIdError,
        exceptions.UnauthorizedError,
    ),
)
async def get_attachments(
    chat_id: pydantic.UUID4,
    limit: pydantic.NonNegativeInt = fastapi.Query(default=10),
    offset: pydantic.NonNegativeInt = fastapi.Query(default=0),
    account_id: str = fastapi.Depends(security.extract_account_id),
    filter_type: typing.Sequence[attachment_entities.AttachmentType] = fastapi.Query(default=[]),
    filter_status: typing.Sequence[attachment_entities.AttachmentStatus] = fastapi.Query(default=[]),
    filter_id: typing.Sequence[pydantic.UUID4] = fastapi.Query(default=[]),
    mediator: cqrs.RequestMediator = fastapi.Depends(dependency=dependencies.request_mediator_factory),
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
            type_filter=list(filter_type),
            status_filter=list(filter_status),
            attachment_id_filter=list(filter_id),
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
