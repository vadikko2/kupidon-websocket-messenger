import cqrs
import fastapi
import pydantic
from fastapi import status
from fastapi_app import response
from fastapi_app.exception_handlers import registry

from domain import exceptions as domain_exceptions
from presentation.api import dependencies
from presentation.api.schema import pagination, validators
from presentation.api.schema.v1 import requests
from service import exceptions as service_exceptions
from service.models.reactions import (
    get_reactors as get_reactors_request,
    react_message,
    unreact_message,
)

router = fastapi.APIRouter(prefix="/reactions", tags=["Reactions"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses=registry.get_exception_responses(
        validators.EmojiValidationError,
        domain_exceptions.TooManyReactions,
        service_exceptions.MessageNotFound,
    ),
)
async def react(
    message_id: pydantic.UUID4,
    account_id: str = fastapi.Depends(dependencies.get_account_id),
    reaction: requests.Reaction = fastapi.Body(...),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> fastapi.Response:
    """
    # Adds reaction
    """
    await mediator.send(
        react_message.ReactMessage(
            message_id=message_id,
            reactor=account_id,
            emoji=reaction.emoji,
        ),
    )
    return fastapi.Response(status_code=status.HTTP_201_CREATED)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=registry.get_exception_responses(
        service_exceptions.MessageNotFound,
    ),
)
async def unreact(
    message_id: pydantic.UUID4,
    reaction: requests.Reaction = fastapi.Body(...),
    account_id: str = fastapi.Depends(dependencies.get_account_id),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> fastapi.Response:
    """
    # Removes reaction
    """
    await mediator.send(
        unreact_message.UnreactMessage(
            message_id=message_id,
            unreactor=account_id,
            reaction=reaction.emoji,
        ),
    )
    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/reactors",
    status_code=status.HTTP_200_OK,
    responses=registry.get_exception_responses(
        service_exceptions.MessageNotFound,
        validators.EmojiValidationError,
        service_exceptions.MessageNotFound,
    ),
)
async def get_reactors(
    message_id: pydantic.UUID4,
    reaction: str = fastapi.Depends(validators.emoji_validator),
    limit: pydantic.NonNegativeInt = fastapi.Query(default=10),
    offset: pydantic.NonNegativeInt = fastapi.Query(default=0),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> response.Response[pagination.Pagination[str]]:
    """
    # Returns reactors for message reaction
    """
    reactors: get_reactors_request.Reactors = await mediator.send(
        get_reactors_request.GetReactors(message_id=message_id, emoji=reaction),
    )
    return response.Response(
        result=pagination.Pagination[str](
            url=f"/v1/messages/{message_id}/reactions/?reaction={reaction}",
            base_items=reactors.reactors,
            limit=limit,
            offset=offset,
        ),
    )
