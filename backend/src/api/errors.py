from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.exceptions import DomainError


def register_error_handlers(app: FastAPI) -> None:
    """Map domain exceptions to HTTP responses once, centrally."""

    @app.exception_handler(DomainError)
    async def _handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
