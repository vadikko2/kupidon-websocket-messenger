import logging
import typing
import uuid

import cqrs
import fastapi
from fastapi_app import response
from fastapi_app.exception_handlers import registry
from starlette import status

from domain import exceptions as domain_exceptions
from presentation import dependencies
from presentation.api.schema import requests, responses, validators
from service import exceptions
from service.requests import (
    apply_message as apply_message_request,
    delete_message as delete_message_request,
    send_message as send_message_request,
)

router = fastapi.APIRouter(prefix="/messages", tags=["Messages"])

logger = logging.getLogger(__name__)


@router.post(
    "/{chat_id}",
    status_code=status.HTTP_201_CREATED,
    responses=registry.get_exception_responses(
        domain_exceptions.DuplicateMessage,
        exceptions.ChatNotFound,
        exceptions.ParticipantNotInChat,
    ),
)
async def send_message(
    chat_id: uuid.UUID,
    account_id: typing.Optional[typing.Text] = fastapi.Header(
        None,
        description="Target account ID",
        alias="UserID",
        example="account-id",
    ),
    reply_to: typing.Optional[uuid.UUID] = fastapi.Body(default=None, examples=[None]),
    content: typing.Text = validators.MessageBody(),
    attachments: typing.List[requests.Attachment] = fastapi.Body(default_factory=list),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.get_request_mediator,
    ),
) -> response.Response[responses.MessageSent]:
    """
    # Send message to receiver
    """
    if account_id is None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UserID header not provided",
        )

    command = send_message_request.SendMessage(
        chat_id=chat_id,
        sender=account_id,
        reply_to=reply_to,
        content=content,
        attachments=[
            send_message_request.Attachment(
                url=attachment.url,
                name=attachment.name,
                content_type=attachment.content_type,
            )
            for attachment in attachments
        ],
    )

    result: send_message_request.MessageSent = await mediator.send(command)

    return response.Response(
        result=responses.MessageSent(
            message_id=result.message_id,
            timestamp=result.created,
        ),
    )


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


@router.put(
    "/{message_id}/delete",
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
