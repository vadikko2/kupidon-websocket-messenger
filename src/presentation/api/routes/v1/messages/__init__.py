import fastapi

from presentation.api.routes.v1.messages import messages, reactions

router = fastapi.APIRouter(prefix="", tags=["Messages"])

router.include_router(messages.router, prefix="/messages/{message_id}")
router.include_router(reactions.router, prefix="/messages/{message_id}")
