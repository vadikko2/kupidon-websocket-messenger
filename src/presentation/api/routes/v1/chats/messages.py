import cqrs
import fastapi
import pydantic
from fastapi import status
from fastapi_app import response
from fastapi_app.exception_handlers import registry

from domain import exceptions as domain_exceptions
from presentation.api import dependencies
from presentation.api.schema import pagination
from presentation.api.schema.v1 import requests, responses
from service import exceptions
from service.models.messages import (
    get_messages as get_messages_request,
    send_message as send_message_request,
    update_message as update_message_request,
)

router = fastapi.APIRouter(prefix="/{chat_id}/messages", tags=["Messages"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses=registry.get_exception_responses(
        exceptions.ChatNotFound,
        exceptions.AttachmentNotFound,
        domain_exceptions.AttachmentAlreadySent,
        exceptions.AttachmentNotForChat,
        exceptions.AttachmentNotForSender,
        exceptions.ParticipantNotInChat,
    ),
)
async def post_message(
    chat_id: pydantic.UUID4,
    account_id: pydantic.StrictStr = fastapi.Depends(dependencies.get_account_id),
    message: requests.PostMessage = fastapi.Body(...),
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
        reply_to=message.reply_to,
        content=message.content,
        attachments=message.attachments,
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
    ),
    description="Публикация сообщений в чате",
)
async def get_messages(
    chat_id: pydantic.UUID4,
    limit: pydantic.NonNegativeInt = fastapi.Query(default=10),
    latest_message_id: pydantic.UUID4 | None = fastapi.Query(default=None),
    reverse: bool = fastapi.Query(default=False),
    account_id: pydantic.StrictStr = fastapi.Depends(dependencies.get_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> response.Response[pagination.MessagesPaginator[get_messages_request.MessageInfo]]:
    """
    # Returns chat messages
    """
    result: get_messages_request.Messages = await mediator.send(
        get_messages_request.GetMessages(
            chat_id=chat_id,
            account=account_id,
            messages_limit=limit,
            latest_message_id=latest_message_id,
            reverse=reverse,
        ),
    )
    return response.Response(
        result=pagination.MessagesPaginator[get_messages_request.MessageInfo](
            url=f"/v1/chats/{chat_id}/messages/",
            base_items=result.messages,
            limit=limit,
            next_id=result.next_message_id,
            previous_id=result.prev_message_id,
            reverse=reverse,
        ),
    )


@router.patch(
    "",
    status_code=status.HTTP_200_OK,
    responses=registry.get_exception_responses(
        exceptions.MessageNotFound,
        exceptions.ParticipantNotInChat,
        exceptions.ChatNotFound,
        exceptions.MessageNotForAccount,
    ),
)
async def edit_message(
    chat_id: pydantic.UUID4,
    account_id: pydantic.StrictStr = fastapi.Depends(dependencies.get_account_id),
    message: requests.UpdateMessage = fastapi.Body(...),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> response.Response[update_message_request.MessageUpdated]:
    """
    # Updates message content
    """
    command = update_message_request.UpdateMessage(
        chat_id=chat_id,
        message_id=message.message_id,
        updater=account_id,
        content=message.content,
        attachments=message.attachments,
    )
    result: update_message_request.MessageUpdated = await mediator.send(command)
    return response.Response(result=result)
