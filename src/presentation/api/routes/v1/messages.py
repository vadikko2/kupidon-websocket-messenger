import logging
import typing
import uuid

import cqrs
import fastapi
from starlette import status

from presentation import dependencies
from presentation.api.schema import requests, responses, validators
from service.commands import (
    apply_message as apply_message_command,
    delete_message as delete_message_command,
    send_message as send_message_command,
)

router = fastapi.APIRouter(prefix="/messages", tags=["Messages"])

logger = logging.getLogger(__name__)


@router.post("/{chat_id}", status_code=status.HTTP_201_CREATED)
async def send_message(
    chat_id: uuid.UUID,
    account_id: typing.Optional[typing.Text] = fastapi.Header(
        None,
        description="Target account ID",
        alias="UserID",
        example="account-id",
    ),
    content: typing.Text = validators.MessageBody(),
    attachments: typing.List[requests.Attachment] = fastapi.Body(default_factory=list),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.get_request_mediator,
    ),
) -> responses.MessageSent:
    """
    # Send message to receiver
    """
    if account_id is None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UserID header not provided",
        )

    command = send_message_command.SendMessage(
        chat_id=chat_id,
        sender=account_id,
        content=content,
        attachments=[
            send_message_command.Attachment(
                url=attachment.url,
                name=attachment.name,
                content_type=attachment.content_type,
            )
            for attachment in attachments
        ],
    )

    result: send_message_command.MessageSent = await mediator.send(command)

    return responses.MessageSent(
        message_id=result.message_id,
        timestamp=result.created,
    )


@router.put("/{message_id}/receive", status_code=status.HTTP_204_NO_CONTENT)
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
        apply_message_command.ApplyMessageReceive(
            message_id=message_id,
            receiver=account_id,
        ),
    )
    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{message_id}/read", status_code=status.HTTP_204_NO_CONTENT)
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
        apply_message_command.ApplyMessageRead(
            message_id=message_id,
            reader=account_id,
        ),
    )
    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{message_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
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
        delete_message_command.DeleteMessage(message_id=message_id, deleter=account_id),
    )
    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)
