import typing

import fastapi
from fastapi import status

import settings

router = fastapi.APIRouter(
    tags=["Service methods"],
)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_version() -> typing.Text:
    """Возвращает версию приложения"""
    return settings.VERSION
