import typing

import cqrs
import fastapi
import pydantic
from fastapi_app.exception_handlers import registry

from domain import events
from presentation.api import dependencies
from service import exceptions

router = fastapi.APIRouter(prefix="/{chat_id}/tap", tags=["Tapping"])


async def send_tap(
    tap: events.TappingInChat,
    emitter: cqrs.EventEmitter = fastapi.Depends(
        dependency=dependencies.event_emitter_factory,
    ),
):
    await emitter.emit(tap)


@router.put(
    "",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    responses=registry.get_exception_responses(
        exceptions.ChatNotFound,
        exceptions.ParticipantNotInChat,
    ),
)
async def tap_into_chat(
    chat_id: pydantic.UUID4,
    background_tasks: fastapi.BackgroundTasks,
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
    background_tasks.add_task(
        send_tap,
        tap=event,
        emitter=emitter,
    )
