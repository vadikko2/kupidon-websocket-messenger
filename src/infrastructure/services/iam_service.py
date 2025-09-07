import logging
import os

import dotenv
import httpx
import httpx_retries

from service import exceptions
from service.interfaces.services import iam_service

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


class HttpIAMService(iam_service.IAMService):
    VALIDATE_TOKEN_ENDPOINT = os.getenv("VALIDATE_TOKEN_ENDPOINT", default="notset")

    def __init__(self):
        self.transport = httpx_retries.RetryTransport(
            retry=httpx_retries.Retry(
                total=15,
                backoff_factor=1,
                status_forcelist=[502, 503, 504, 429],
                allowed_methods=["POST", "GET"],
            ),
        )

    async def get_user_id(self, token: str) -> str:
        logger.info("Validating token")
        try:
            async with httpx.AsyncClient(
                transport=self.transport,
            ) as client:
                response = await client.get(
                    self.VALIDATE_TOKEN_ENDPOINT,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}",
                    },
                    timeout=30.0,
                )
        except httpx.HTTPError as e:
            logger.error(f"Failed to get user id: {e}")
            raise exceptions.GetUserIdError(f"Failed to get user id: {str(e)}")

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get user id: {e}")
            response_data = response.json()
            raise exceptions.UnauthorizedError(response_data.get("message", "unknown"))

        response_data = response.json()

        return response_data["result"]["user_id"]
