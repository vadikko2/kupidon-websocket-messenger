import fastapi

from presentation.api.routes.v1.chats import attachments, chats, messages

router = fastapi.APIRouter(prefix="")

router.include_router(chats.router, prefix="/chats")
router.include_router(messages.router, prefix="/chats")
router.include_router(attachments.router, prefix="/chats")
