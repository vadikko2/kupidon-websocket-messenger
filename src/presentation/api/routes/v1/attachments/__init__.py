import fastapi

from presentation.api.routes.v1.attachments import attachments, image, voice, circle

router = fastapi.APIRouter(prefix="/{chat_id}", tags=["Attachments"])

router.include_router(attachments.router, prefix="/attachments")
router.include_router(voice.router, prefix="/attachments/voice")
router.include_router(image.router, prefix="/attachments/image")
router.include_router(circle.router, prefix="/attachments/circle")
