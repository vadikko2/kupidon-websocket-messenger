import logging
import typing

import cqrs
import fastapi
import pydantic
from fastapi import status
from fastapi_app import response
from fastapi_app.exception_handlers import registry

from presentation.api import dependencies
from service import exceptions
from service.requests.messages import (
    apply_message as apply_message_request,
    delete_message as delete_message_request,
    get_messages as get_messages_request,
)

router = fastapi.APIRouter(prefix="", tags=["Messages"])

logger = logging.getLogger(__name__)


@router.put(
    "/read",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=registry.get_exception_responses(
        exceptions.ChatNotFound,
        exceptions.MessageNotFound,
    ),
)
async def apply_message_read(
    message_id: pydantic.UUID4,
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> fastapi.Response:
    """
    # Apply message as read
    """
    await mediator.send(
        apply_message_request.ApplyMessage(
            applier=account_id,
            message_id=message_id,
        ),
    )
    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=registry.get_exception_responses(
        exceptions.ChatNotFound,
        exceptions.MessageNotFound,
        exceptions.ParticipantNotInChat,
    ),
)
async def delete_message(
    message_id: pydantic.UUID4,
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> fastapi.Response:
    """
    # Deletes message
    """
    await mediator.send(
        delete_message_request.DeleteMessage(
            message_id=message_id,
            deleter=account_id,
        ),
    )
    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/preview",
    status_code=status.HTTP_200_OK,
    responses=registry.get_exception_responses(
        exceptions.MessageNotFound,
        exceptions.ParticipantNotInChat,
        exceptions.ChatNotFound,
    ),
)
async def get_message_preview(
    message_id: pydantic.UUID4,
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> response.Response[get_messages_request.MessagePreview]:
    """
    # Returns message preview by message id
    """
    message: get_messages_request.MessagePreview = await mediator.send(
        get_messages_request.GetMessagePreview(
            message_id=message_id,
            account=account_id,
        ),
    )
    return response.Response(result=message)
