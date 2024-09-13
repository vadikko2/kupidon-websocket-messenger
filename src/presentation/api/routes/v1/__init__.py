import fastapi

from presentation.api.routes.v1 import chats, messages, subscription

v1_router = fastapi.APIRouter(prefix="/v1")

v1_router.include_router(chats.router)
v1_router.include_router(messages.router)
v1_router.include_router(subscription.router)
