from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.alerts.models  # noqa: F401  register ORM classes on Base.metadata
import src.files.models  # noqa: F401
from src.alerts.router import router as alerts_router
from src.api.errors import register_error_handlers
from src.core.config import get_settings
from src.files.router import router as files_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="File manager")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)
    app.include_router(files_router)
    app.include_router(alerts_router)

    @app.get("/health", tags=["system"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
