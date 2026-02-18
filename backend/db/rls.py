"""
RLS (Row-Level Security) middleware for FastAPI.
Sets the PostgreSQL session variable app.tenant_id from the X-Tenant-ID header
so that RLS policies automatically filter rows per tenant.
"""

import logging
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy import text

logger = logging.getLogger("nadakki.rls")

DEFAULT_TENANT = "credicefi"


class RLSMiddleware(BaseHTTPMiddleware):
    """
    Reads X-Tenant-ID from the request header and stores it on request.state
    so downstream code can use it for SET LOCAL app.tenant_id.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        tenant_id = request.headers.get("x-tenant-id", DEFAULT_TENANT)
        request.state.tenant_id = tenant_id
        response = await call_next(request)
        return response
