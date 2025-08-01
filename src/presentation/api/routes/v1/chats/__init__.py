import fastapi

from presentation.api.routes.v1 import attachments
from presentation.api.routes.v1.chats import chats, messages, tags, tapping

router = fastapi.APIRouter(prefix="")

router.include_router(chats.router, prefix="/chats")
router.include_router(messages.router, prefix="/chats")
router.include_router(attachments.router, prefix="/chats")
router.include_router(tapping.router, prefix="/chats")
router.include_router(tags.router, prefix="/chats")
