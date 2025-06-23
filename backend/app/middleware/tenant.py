from app.config.settings import settings
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from urllib.parse import urlparse
from app.db.session import get_master_session, get_tenant_session
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
        
        # Extract subdomain (api.edutenant.localhost -> "api")
        subdomain = host.replace(f".{self.base_domain}", "").split(":")[0].strip().lower()

        # Global context (api.edutenant.localhost)
        if subdomain == self.global_prefix:
            request.state.context = "global"
            request.state.tenant_id = None
            logger.debug("Global context detected")
            
            async with get_master_session() as session:
                request.state.session = session
                return await call_next(request)

        # Tenant context (tenant1.edutenant.localhost)
        if "." in subdomain:  # Invalid if contains multiple dots
            return JSONResponse(status_code=400, content={"detail": "Invalid subdomain format"})

        # Verify tenant exists
        async with get_master_session() as session:
            tenant_exists = await session.scalar(
                text("SELECT 1 FROM public.tenants WHERE subdomain = :subdomain"),
                {"subdomain": subdomain}
            )
            if not tenant_exists:
                return JSONResponse(status_code=404, content={"detail": f"Tenant '{subdomain}' not found"})

        request.state.tenant_id = subdomain
        request.state.context = "tenant"
        logger.debug(f"Tenant context detected: '{subdomain}'")

        async with get_tenant_session(subdomain) as tenant_session:
            request.state.session = tenant_session
            return await call_next(request)
