
from contextlib import asynccontextmanager

from requests import Request

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings 
from app.db.init_db import init_db

from fastapi.routing import APIRoute
from app.utils.errors import register_all_errors
from app.db.session import clear_engine_cache
from app.middleware.tenant import TenantSubdomainMiddleware
from app.apis.global_router import global_router
from app.apis.tenant_router import tenant_router


from app.apis.openai_routes import get_docs_router


def custom_generate_unique_id(route: APIRoute) -> str:
    tag = route.tags[0] if route.tags else "default"
    return f"{tag}-{route.name}"


@asynccontextmanager
async def life_span(app: FastAPI):
    print("server is starting ...")
    await clear_engine_cache()
    await init_db()
    yield
    print("server has been stopped")


app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=None,                # Disable default docs
    openapi_url=None,             # Disable default OpenAPI
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=life_span,
)

# CORS setup
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Custom tenant/global middleware
app.add_middleware(
    TenantSubdomainMiddleware,
    base_domain="edutenant.localhost",
    global_prefix="api",
)



register_all_errors(app)


app.include_router(get_docs_router(app))



# Global routes (tenant registration, auth)
app.include_router(global_router, prefix=f"{settings.API_V1_STR}")

# Tenant-specific routes (school logic)
# app.include_router(tenant_router, prefix=f"{settings.API_V1_STR}/tenants")

@app.middleware("http")
async def tenant_routes_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # Only mount tenant router if we're in tenant context
    if getattr(request.state, "context", None) == "tenant":
        tenant_id = request.state.tenant_id
        app.include_router(
            tenant_router,
            prefix=f"{settings.API_V1_STR}/tenants/{tenant_id}"
        )
    
    return response