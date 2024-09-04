import logging
import typing
import uuid

import cqrs
import fastapi
from fastapi_app.exception_handlers import registry
from starlette import status

from presentation import dependencies
from service import exceptions
from service.requests import (
    apply_message as apply_message_request,
    delete_message as delete_message_request,
)

router = fastapi.APIRouter(prefix="/messages", tags=["Messages"])

logger = logging.getLogger(__name__)


@router.put(
    "/{message_id}/receive",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=registry.get_exception_responses(
        exceptions.ChatNotFound,
        exceptions.MessageNotFound,
        exceptions.ChangeStatusAccessDonated,
    ),
)
async def apply_message_receive(
    message_id: uuid.UUID,
    account_id: typing.Optional[typing.Text] = fastapi.Header(
        None,
        description="Target account ID",
        alias="UserID",
        example="account-id",
    ),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.get_request_mediator,
    ),
) -> fastapi.Response:
    """
    # Apply message as received
    """
    if account_id is None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UserID header not provided",
        )

    await mediator.send(
        apply_message_request.ApplyMessageReceive(
            message_id=message_id,
            receiver=account_id,
        ),
    )
    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/{message_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=registry.get_exception_responses(
        exceptions.ChatNotFound,
        exceptions.MessageNotFound,
        exceptions.ChangeStatusAccessDonated,
    ),
)
async def apply_message_read(
    message_id: uuid.UUID,
    account_id: typing.Optional[typing.Text] = fastapi.Header(
        None,
        description="Target account ID",
        alias="UserID",
        example="account-id",
    ),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.get_request_mediator,
    ),
) -> fastapi.Response:
    """
    # Apply message as read
    """
    if account_id is None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UserID header not provided",
        )

    await mediator.send(
        apply_message_request.ApplyMessageRead(
            message_id=message_id,
            reader=account_id,
        ),
    )
    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=registry.get_exception_responses(
        exceptions.ChatNotFound,
        exceptions.MessageNotFound,
        exceptions.ChangeStatusAccessDonated,
    ),
)
async def delete_message(
    message_id: uuid.UUID,
    account_id: typing.Optional[typing.Text] = fastapi.Header(
        None,
        description="Target account ID",
        alias="UserID",
        example="account-id",
    ),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.get_request_mediator,
    ),
) -> fastapi.Response:
    """
    # Apply message as read
    """
    if account_id is None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UserID header not provided",
        )

    await mediator.send(
        delete_message_request.DeleteMessage(message_id=message_id, deleter=account_id),
    )
    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)
