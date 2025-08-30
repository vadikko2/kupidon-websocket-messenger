import cqrs

from domain import reactions
from service import exceptions
from service.interfaces import unit_of_work
from service.models.reactions import react_message
from service.validators import messages as message_validators


class ReactMessageHandler(cqrs.RequestHandler[react_message.ReactMessage, None]):
    def __init__(self, uow: unit_of_work.UoW):
        self.uow = uow

    @property
    def events(self):
        return list(self.uow.get_events())

    async def handle(self, request: react_message.ReactMessage) -> None:
        async with self.uow:
            message = await self.uow.message_repository.get(request.message_id)
            if not message:
                raise exceptions.MessageNotFound(request.message_id)
            message_validators.raise_if_message_deleted(message)

            new_reaction = reactions.Reaction(
                message_id=request.message_id,
                reactor=request.reactor,
                emoji=request.emoji,
            )
            message.react(new_reaction)

            await self.uow.message_repository.update(message)
            await self.uow.commit()
