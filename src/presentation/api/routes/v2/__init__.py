import fastapi

from presentation.api.routes.v2 import chats

v2_router = fastapi.APIRouter(prefix="/v2")

v2_router.include_router(chats.router, prefix="/chats")
