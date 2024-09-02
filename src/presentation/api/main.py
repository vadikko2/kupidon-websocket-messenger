import fastapi

from presentation.api import routes

app = fastapi.FastAPI(title="Kupidon messanger")

app.include_router(routes.outgoing.router)
app.include_router(routes.incoming.router)
