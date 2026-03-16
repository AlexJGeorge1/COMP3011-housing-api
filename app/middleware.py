"""
Global error handling middleware.

Catches unhandled exceptions and returns consistent JSON error responses
instead of exposing raw Python tracebacks to clients.
"""

import logging
import time
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("housing_api")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        try:
            response = await call_next(request)
            duration = round((time.time() - start) * 1000, 1)
            logger.info(
                "%s %s → %s (%sms)",
                request.method,
                request.url.path,
                response.status_code,
                duration,
            )
            return response
        except Exception as exc:
            duration = round((time.time() - start) * 1000, 1)
            logger.exception(
                "Unhandled error on %s %s (%sms): %s",
                request.method,
                request.url.path,
                duration,
                exc,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "detail": "An unexpected error occurred. Please try again or contact support.",
                },
            )
