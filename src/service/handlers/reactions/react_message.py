import cqrs

from domain import messages, reactions
from service import exceptions, unit_of_work
from service.requests.reactions import react_message


class ReactMessageHandler(cqrs.RequestHandler[react_message.ReactMessage, None]):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self):
        return self.uow.get_events()

    async def handle(self, request: react_message.ReactMessage) -> None:
        async with self.uow:
            message = await self.uow.message_repository.get(request.message_id)

            if message is None or message.status == messages.MessageStatus.DELETED:
                raise exceptions.MessageNotFound(request.message_id)

            new_reaction = reactions.Reaction(
                message_id=request.message_id,
                reactor=request.reactor,
                emoji=request.emoji,
            )
            message.react(new_reaction)

            await self.uow.message_repository.update(message)
            await self.uow.commit()
