import cqrs
from cqrs.events import event

from domain import messages as messages_entity
from service import exceptions, unit_of_work
from service.requests import get_history


class GetHistoryHandler(
    cqrs.RequestHandler[get_history.GetHistory, get_history.History],
):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow
        self._events = []

    @property
    def events(self) -> list[event.Event]:
        return self._events

    async def handle(self, request: get_history.GetHistory) -> get_history.History:
        async with self.uow:
            chat_history = await self.uow.chat_repository.get_chat_history(
                chat_id=request.chat_id,
                messages_limit=request.messages_limit,
                latest_message_id=request.latest_message_id,
            )

            if chat_history is None:
                raise exceptions.ChatNotFound(request.chat_id)

            if request.account not in chat_history.participants:
                raise exceptions.ParticipantNotInChat(
                    request.account,
                    chat_history.chat_id,
                )

            messages = []

            for message in chat_history.history:
                if message.status == messages_entity.MessageStatus.DELETED:
                    continue

                messages.append(message)
                message.deliver(request.account)

        self._events += self.uow.get_events()
        return get_history.History(messages=messages)
