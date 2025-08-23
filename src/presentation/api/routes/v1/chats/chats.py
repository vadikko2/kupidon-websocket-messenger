import logging
import typing

import cqrs
import fastapi
import pydantic
from fastapi import status
from fastapi_app import response
from fastapi_app.exception_handlers import registry

from presentation.api import dependencies
from presentation.api.schema import pagination
from presentation.api.schema.v1 import requests, responses
from service import exceptions
from service.requests.chats import (
    delete_chat as delete_chat_request,
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
    status_code=status.HTTP_200_OK,
)
async def get_chats(
    limit: pydantic.NonNegativeInt = fastapi.Query(default=10),
    offset: pydantic.NonNegativeInt = fastapi.Query(default=0),
    chat_id: typing.List[pydantic.UUID4] = fastapi.Query(default=[], description="Chat ids"),
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    with_participant_id: typing.List[typing.Text] = fastapi.Query(
        default=[],
        description="Participant ids",
        max_length=10,
    ),
    strict_participants_search: pydantic.StrictBool = fastapi.Query(
        default=False,
        description="Strict participants search",
    ),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> response.Response[pagination.Pagination[get_chats_request.ChatInfo]]:
    """
    # Returns chat with specified participant
    """
    result: get_chats_request.Chats = await mediator.send(
        get_chats_request.GetChats(
            participant=account_id,
            chat_ids=chat_id if chat_id else None,
            with_participant_ids=with_participant_id if with_participant_id else None,
            strict_participants_search=strict_participants_search,
        ),
    )
    return response.Response(
        result=pagination.Pagination[get_chats_request.ChatInfo](
            url="/chats/?",
            base_items=result.chats,
            limit=limit,
            offset=offset,
            count=len(result.chats),
        ),
    )


@router.delete(
    "/{chat_id}",
    tags=["Chats"],
    status_code=status.HTTP_204_NO_CONTENT,
    responses=registry.get_exception_responses(
        exceptions.ChatNotFound,
        exceptions.ParticipantNotInChat,
    ),
)
async def delete_chat(
    chat_id: pydantic.UUID4,
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> None:
    """
    # Deletes chat for specified account
    """
    await mediator.send(
        delete_chat_request.DeleteChat(
            chat_id=chat_id,
            actor=account_id,
        ),
    )
