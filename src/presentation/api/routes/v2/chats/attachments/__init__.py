import fastapi

from presentation.api.routes.v2.chats.attachments import voice

router = fastapi.APIRouter(prefix="/{chat_id}/attachments", tags=["Attachments"])

router.include_router(voice.router)
