import abc
import typing


class MessageBroker(abc.ABC):

    @abc.abstractmethod
    async def start(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def send_message(self, receiver: typing.Text, message: bytes) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_message(self) -> bytes | None:
        raise NotImplementedError

    @abc.abstractmethod
    async def subscribe(self, receiver: typing.Text) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def unsubscribe(self, receiver: typing.Text) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def stop(self) -> None:
        raise NotImplementedError
