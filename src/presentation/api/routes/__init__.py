from presentation.api.routes import healthcheck
from presentation.api.routes.v1 import v1_router
from presentation.api.routes.v2 import v2_router

__all__ = [
    "v1_router",
    "v2_router",
    "healthcheck",
]
