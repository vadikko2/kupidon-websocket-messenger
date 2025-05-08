import fastapi

from presentation.api.routes.v2.chats import attachments

router = fastapi.APIRouter(prefix="")

router.include_router(attachments.router)
