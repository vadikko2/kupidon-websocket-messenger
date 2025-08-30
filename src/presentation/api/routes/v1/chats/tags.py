import cqrs
import fastapi
import pydantic
from fastapi_app.exception_handlers import registry

from presentation.api import dependencies
from presentation.api.schema.v1 import requests
from service import exceptions
from service.models.chats import add_tag, remove_tag

router = fastapi.APIRouter(prefix="/{chat_id}/tags", tags=["Tags"])


@router.post(
    "",
    tags=["Tags"],
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    responses=registry.get_exception_responses(
        exceptions.ChatNotFound,
        exceptions.ParticipantNotInChat,
    ),
)
async def add_chat_tag(
    chat_id: pydantic.UUID4,
    account_id: str = fastapi.Depends(dependencies.get_account_id),
    tag: requests.ChatTag = fastapi.Body(...),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
):
    """
    Creates chat tag
    """
    await mediator.send(
        add_tag.AddTag(
            chat_id=chat_id,
            account_id=account_id,
            tag=tag.tag,
        ),
    )


@router.delete(
    "",
    tags=["Tags"],
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    responses=registry.get_exception_responses(
        exceptions.ChatNotFound,
        exceptions.ParticipantNotInChat,
    ),
)
async def remove_chat_tag(
    chat_id: pydantic.UUID4,
    account_id: str = fastapi.Depends(dependencies.get_account_id),
    tag: requests.ChatTag = fastapi.Body(...),
    mediator: cqrs.RequestMediator = fastapi.Depends(
        dependency=dependencies.request_mediator_factory,
    ),
):
    """
    Removes chat tag
    """
    await mediator.send(
        remove_tag.RemoveTag(
            chat_id=chat_id,
            account_id=account_id,
            tag=tag.tag,
        ),
    )
