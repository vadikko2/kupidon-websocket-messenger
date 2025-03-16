import typing
import uuid

import cqrs
import fastapi
from fastapi_app.exception_handlers import registry

from domain import events
from presentation.api import dependencies
from service import exceptions

router = fastapi.APIRouter(prefix="/{chat_id}/tap", tags=["Tapping"])


@router.put(
    "",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    responses=registry.get_exception_responses(
        exceptions.ChatNotFound,
        exceptions.ParticipantNotInChat,
    ),
)
async def tap(
    chat_id: uuid.UUID,
    account_id: typing.Text = fastapi.Depends(dependencies.get_account_id),
    emitter: cqrs.EventEmitter = fastapi.Depends(
        dependency=dependencies.event_emitter_factory,
    ),
):
    """
    Tap in chat
    """
    event = events.TappingInChat(
        chat_id=chat_id,
        account_id=account_id,
    )
    await emitter.emit(event)
