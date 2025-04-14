from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from urllib.parse import urlparse
from app.db.session import get_master_session
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class TenantSubdomainMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, base_domain: str, global_prefix: str):
        super().__init__(app)
        self.base_domain = base_domain
        self.global_prefix = global_prefix

    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host", "")
        subdomain = host.replace(f".{self.base_domain}", "").split(":")[0]

        # Check for global context
        if subdomain == self.global_prefix:
            request.state.context = "global"
            request.state.tenant_id = None
            logger.debug("Global context detected.")
            return await call_next(request)

        # Invalid or missing tenant subdomain
        if not subdomain or subdomain == self.base_domain:
            return JSONResponse(status_code=400, content={"detail": "Tenant subdomain not detected"})

        # Check tenant exists
        async with get_master_session() as session:
            result = await session.execute(
                text("SELECT 1 FROM public.tenants WHERE domain = :domain"),
                {"domain": subdomain}
            )
            if not result.scalar():
                return JSONResponse(status_code=404, content={"detail": f"Tenant '{subdomain}' not found"})

        # Valid tenant context
        request.state.tenant_id = subdomain
        request.state.context = "tenant"
        logger.debug(f"Tenant context detected: '{subdomain}'")
        return await call_next(request)

