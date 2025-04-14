from fastapi import APIRouter, Depends
from app.domains.auth.apis.login_router import auth_router
from app.domains.school.apis.tenant import tenant_router
from app.config.tenant_dependencies import require_global_context

global_router = APIRouter(dependencies=[Depends(require_global_context)])
global_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
global_router.include_router(tenant_router, prefix="/tenants", tags=["Tenants"])
