import logging
import sys
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

# Sensitive headers and fields to redact
REDACTED_HEADERS = {"authorization", "x-api-key", "cookie", "set-cookie"}


def setup_logging() -> None:
    """Configures application-wide structured logging."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Avoid duplicate handlers if re-initialized
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        root_logger.handlers = [handler]


logger = logging.getLogger("placement_coach")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for non-sensitive logging of incoming HTTP requests & duration."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        client_host = request.client.host if request.client else "unknown"
        
        logger.info(
            f"Incoming {request.method} {request.url.path} from {client_host}"
        )
        
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                f"Completed {request.method} {request.url.path} - "
                f"Status: {response.status_code} in {duration_ms:.2f}ms"
            )
            return response
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"Failed {request.method} {request.url.path} after {duration_ms:.2f}ms: {exc}",
                exc_info=True,
            )
            raise exc
