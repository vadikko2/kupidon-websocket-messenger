import logging
import typing
import uuid

import cqrs
import fastapi
import pydantic
from fastapi_app import response
from fastapi_app.exception_handlers import registry
from starlette import status

from presentation import dependencies
from presentation.api.schema import responses
from service import exceptions
from service.commands import open_chat as open_chat_command
from service.queries import (
    get_chats as get_chats_query,
    get_history as get_history_query,
)

router = fastapi.APIRouter(prefix="/chats", tags=["Chats"])

logger = logging.getLogger(__name__)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def open_chat(
    participants: typing.List[typing.Text] = fastapi.Body(
        ...,
        examples=[["account-id-1", "account-id-2"]],
    ),
    name: typing.Optional[typing.Text] = fastapi.Body(None, examples=["Chat name"]),
    account_id: typing.Optional[typing.Text] = fastapi.Header(
        None,
        description="Target account ID",
        alias="UserID",
        example="account-id",
    ),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.get_request_mediator,
    ),
) -> response.Response[responses.ChatCreated]:
    """
    # Opens chat with specified participant
    """
    if account_id is None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UserID header not provided",
        )

    result: open_chat_command.ChatOpened = await mediator.send(
        open_chat_command.OpenChat(
            initiator=account_id,
            participants=participants,
            name=name,
        ),
    )
    return response.Response(result=responses.ChatCreated(chat_id=result.chat_id))


@router.get("/", status_code=status.HTTP_201_CREATED)
async def get_chats(
    limit: pydantic.NonNegativeInt = fastapi.Query(default=10),
    offset: pydantic.NonNegativeInt = fastapi.Query(default=0),
    account_id: typing.Optional[typing.Text] = fastapi.Header(
        None,
        description="Target account ID",
        alias="UserID",
        example="account-id",
    ),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.get_request_mediator,
    ),
) -> response.Response[responses.ChatList]:
    """
    # Returns chat with specified participant
    """
    if account_id is None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UserID header not provided",
        )

    result: get_chats_query.Chats = await mediator.send(
        get_chats_query.GetChats(
            participant=account_id,
            limit=limit,
            offset=offset,
        ),
    )
    return response.Response(
        result=responses.ChatList(
            chats=[
                responses.ChatInfo(
                    chat_id=chat.chat_id,
                    name=chat.name,
                    last_activity_timestamp=chat.last_activity_timestamp,
                    last_message_id=chat.last_message,
                )
                for chat in result.chats
            ],
            limit=limit,
            offset=offset,
        ),
    )


@router.get(
    "/history/{chat_id}",
    status_code=status.HTTP_200_OK,
    responses=registry.get_exception_responses(
        exceptions.ChatNotFound,
        exceptions.ParticipantNotInChat,
        exceptions.ChangeStatusAccessDonated,
    ),
)
async def get_history(
    chat_id: uuid.UUID,
    limit: pydantic.NonNegativeInt = fastapi.Query(default=10),
    latest_message_id: uuid.UUID | None = fastapi.Query(default=None),
    account_id: typing.Optional[typing.Text] = fastapi.Header(
        None,
        description="Target account ID",
        alias="UserID",
        example="account-id",
    ),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.get_request_mediator,
    ),
) -> response.Response[responses.HistoryPage]:
    """
    # Returns chat history
    """
    if account_id is None:
        raise fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UserID header not provided",
        )

    result: get_history_query.History = await mediator.send(
        get_history_query.GetHistory(
            chat_id=chat_id,
            account=account_id,
            messages_limit=limit,
            latest_message_id=latest_message_id,
        ),
    )
    return response.Response(
        result=responses.HistoryPage(
            chat_id=chat_id,
            messages=result.messages,
            limit=limit,
            latest_id=result.messages[-1].message_id if result.messages else None,
        ),
    )
