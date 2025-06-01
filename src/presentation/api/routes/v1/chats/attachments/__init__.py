import fastapi

from presentation.api.routes.v1.chats.attachments import attachments, voice, image

router = fastapi.APIRouter(prefix="/{chat_id}", tags=["Attachments"])

router.include_router(attachments.router, prefix="/attachments")
router.include_router(voice.router, prefix="/attachments/voice")
router.include_router(image.router, prefix="/attachments/image")
