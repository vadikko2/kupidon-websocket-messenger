import typing
import uuid

import cqrs
import fastapi
import pydantic
from fastapi import status
from fastapi_app import response
from fastapi_app.exception_handlers import registry

from domain import exceptions as domain_exceptions
from presentation import dependencies
from presentation.api.schema import pagination, responses, validators
from service import exceptions
from service.requests.messages import (
    get_messages as get_messages_request,
    send_message as send_message_request,
)

router = fastapi.APIRouter(prefix="/{chat_id}/messages", tags=["Messages"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses=registry.get_exception_responses(
        domain_exceptions.DuplicateMessage,
        exceptions.ChatNotFound,
        exceptions.AttachmentNotFound,
        exceptions.AttachmentNotForChat,
        exceptions.AttachmentNotForSender,
        exceptions.ParticipantNotInChat,
    ),
)
async def send_message(
    chat_id: uuid.UUID,
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    reply_to: typing.Optional[uuid.UUID] = fastapi.Body(default=None, examples=[None]),
    content: typing.Text = validators.MessageBody(),
    attachments: typing.List[uuid.UUID] = fastapi.Body(
        default_factory=list,
        max_length=5,
        examples=[[]],
    ),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> response.Response[responses.MessageSent]:
    """
    # Send message to receiver
    """
    command = send_message_request.SendMessage(
        chat_id=chat_id,
        sender=account_id,
        reply_to=reply_to,
        content=content,
        attachments=attachments,
    )

    result: send_message_request.MessageSent = await mediator.send(command)

    return response.Response(
        result=responses.MessageSent(
            message_id=result.message_id,
            timestamp=result.created,
        ),
    )


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses=registry.get_exception_responses(
        exceptions.ChatNotFound,
        exceptions.ParticipantNotInChat,
        exceptions.ChangeStatusAccessDonated,
    ),
)
async def get_messages(
    chat_id: uuid.UUID,
    limit: pydantic.NonNegativeInt = fastapi.Query(default=10),
    latest_message_id: uuid.UUID | None = fastapi.Query(default=None),
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> response.Response[pagination.Pagination[get_messages_request.MessageInfo]]:
    """
    # Returns chat messages
    """
    result: get_messages_request.Messages = await mediator.send(
        get_messages_request.GetMessages(
            chat_id=chat_id,
            account=account_id,
            messages_limit=limit,
            latest_message_id=latest_message_id,
        ),
    )
    return response.Response(
        result=pagination.Pagination[get_messages_request.MessageInfo](
            url=f"/chats/{chat_id}/messages/?latest_id={result.messages[-1].message_id if result.messages else None}",
            base_items=result.messages,
            limit=limit,
        ),
    )
