"""
Global rate limiting middleware — 100 requests/min per tenant.
Adds X-RateLimit-Remaining header. Returns 429 if exceeded.
"""

import time
import threading
import logging
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

logger = logging.getLogger("nadakki.rate_limit")

_MAX_REQUESTS = 100
_WINDOW_SECONDS = 60

_buckets: dict = defaultdict(list)
_lock = threading.Lock()


class GlobalRateLimitMiddleware(BaseHTTPMiddleware):
    """100 requests/min per tenant. Adds X-RateLimit-Remaining header."""

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # Skip health and docs
        if path in ("/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"):
            return await call_next(request)

        tenant = request.headers.get("x-tenant-id", "credicefi")
        now = time.time()
        cutoff = now - _WINDOW_SECONDS

        with _lock:
            _buckets[tenant] = [t for t in _buckets[tenant] if t > cutoff]
            count = len(_buckets[tenant])

            if count >= _MAX_REQUESTS:
                remaining = 0
                return JSONResponse(
                    status_code=429,
                    content={"error": "Rate limit exceeded", "retry_after_seconds": _WINDOW_SECONDS},
                    headers={
                        "X-RateLimit-Limit": str(_MAX_REQUESTS),
                        "X-RateLimit-Remaining": "0",
                        "Retry-After": str(_WINDOW_SECONDS),
                    },
                )

            _buckets[tenant].append(now)
            remaining = _MAX_REQUESTS - count - 1

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(_MAX_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
