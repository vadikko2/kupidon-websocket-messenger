import abc


class IAMService(abc.ABC):
    @abc.abstractmethod
    async def get_user_id(self, token: str) -> str:
        """
        Returns user id
        :raises: service.exceptions.UnauthorizedError
        :raises: service.exceptions.GetUserIdError
        """
        raise NotImplementedError
