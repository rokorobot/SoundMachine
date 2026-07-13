"""Operator-safe typed errors (R41/T10): stable codes, never a traceback or
raw exception string in the response body."""
import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

logger = logging.getLogger("sound_machina")


class APIError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


def _envelope(code: str, message: str):
    return {"error": {"code": code, "message": message}}


def install_error_handlers(app):
    @app.exception_handler(APIError)
    async def _api_error(_: Request, exc: APIError):
        return JSONResponse(status_code=exc.status_code, content=_envelope(exc.code, exc.message))

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError):
        # Summarize which fields failed without leaking internals.
        fields = sorted({".".join(str(p) for p in e.get("loc", []) if p != "body") for e in exc.errors()})
        msg = "Invalid request payload" + (f": {', '.join(f for f in fields if f)}" if any(fields) else "")
        return JSONResponse(status_code=422, content=_envelope("VALIDATION_FAILED", msg))

    @app.exception_handler(Exception)
    async def _unexpected(_: Request, exc: Exception):
        logger.exception("Unhandled error")  # details to server log only
        return JSONResponse(status_code=500, content=_envelope("INTERNAL", "Internal server error"))
