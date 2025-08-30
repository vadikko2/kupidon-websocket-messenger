import fastapi

from presentation.api.routes.v1 import chats, messages, subscription

router = fastapi.APIRouter(prefix="/v1")

router.include_router(chats.router)
router.include_router(messages.router)
router.include_router(subscription.router)
