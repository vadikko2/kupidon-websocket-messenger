import typing
import uuid

import cqrs
import fastapi
from fastapi import status
from fastapi_app.exception_handlers import registry

from domain import exceptions as domain_exceptions
from presentation import dependencies
from presentation.api.schema import requests
from service import exceptions as service_exceptions
from service.requests import react_message

router = fastapi.APIRouter(prefix="/reactions")


@router.post(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=registry.get_exception_responses(
        requests.EmojiValidationError,
        domain_exceptions.TooManyReactions,
        service_exceptions.MessageNotFound,
    ),
)
async def react(
    message_id: uuid.UUID,
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    reaction: requests.Reaction = fastapi.Body(...),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> fastapi.Response:
    """
    # Add reaction
    """
    await mediator.send(
        react_message.ReactMessage(
            message_id=message_id,
            reactor=account_id,
            emoji=reaction.emoji,
        ),
    )
    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{reaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unreact(
    message_id: uuid.UUID,
    reaction_id: uuid.UUID,
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    reaction: requests.Reaction = fastapi.Body(...),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
) -> fastapi.Response:
    """
    # Remove reaction
    """
    return fastapi.Response(status_code=status.HTTP_204_NO_CONTENT)
