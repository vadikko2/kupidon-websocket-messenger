import logging
import typing

import cqrs
import fastapi
import pydantic
from fastapi import status
from fastapi_app import response

from presentation.api import dependencies
from presentation.api.schema import pagination, requests, responses
from service.requests.chats import (
    get_chats as get_chats_request,
    open_chat as open_chat_request,
)

router = fastapi.APIRouter(prefix="")

logger = logging.getLogger(__name__)


@router.post(
    "",
    tags=["Chats"],
    status_code=status.HTTP_201_CREATED,
)
async def open_chat(
    body: requests.CreateChat = fastapi.Body(),
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> response.Response[responses.ChatCreated]:
    """
    # Opens chat with specified participant
    """
    result: open_chat_request.ChatOpened = await mediator.send(
        open_chat_request.OpenChat(
            initiator=account_id,
            participants=body.participants,
            name=body.name,
            avatar=body.avatar,
        ),
    )
    return response.Response(result=responses.ChatCreated(chat_id=result.chat_id))


@router.get(
    "",
    tags=["Chats"],
    status_code=status.HTTP_201_CREATED,
)
async def get_chats(
    limit: pydantic.NonNegativeInt = fastapi.Query(default=10),
    offset: pydantic.NonNegativeInt = fastapi.Query(default=0),
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> response.Response[pagination.Pagination[get_chats_request.ChatInfo]]:
    """
    # Returns chat with specified participant
    """
    result: get_chats_request.Chats = await mediator.send(
        get_chats_request.GetChats(participant=account_id),
    )
    return response.Response(
        result=pagination.Pagination[get_chats_request.ChatInfo](
            url="/chats/?",
            base_items=result.chats,
            limit=limit,
            offset=offset,
        ),
    )
