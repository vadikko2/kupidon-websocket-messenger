import typing
import uuid

from domain import message as message_entity
from infrastructure.database.persistent import protocol


class SqlAlchemyMessageRepository(protocol.MessageRepository):

    async def get_new_messages(self, receiver: typing.Text) -> typing.List[message_entity.Message]:
        pass

    async def add(self, message: message_entity.Message) -> None:
        pass

    async def get(self, message_id: uuid.UUID) -> message_entity.Message | None:
        pass

    async def change_status(self, message_id: uuid.UUID, status: message_entity.MessageStatus) -> None:
        pass

    async def commit(self):
        pass

    async def rollback(self):
        pass
