from fastapi import APIRouter, Depends
from app.domains.auth.apis.login_router import auth_router
from app.domains.school.apis.tenant import tenant_management_router
from app.domains.auth.apis.users_router import user_router
from app.domains.auth.apis.role import role_router
from app.domains.auth.apis.permission import permission_router
from app.config.tenant_dependencies import require_global_context

global_router = APIRouter(dependencies=[Depends(require_global_context)])
global_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
global_router.include_router(tenant_management_router, prefix="/tenants", tags=["Tenants management"])
global_router.include_router(user_router, prefix="/users", tags=["Users"])
global_router.include_router(role_router, prefix="/roles", tags=["Roles"])
global_router.include_router(permission_router, prefix="/permissions", tags=["Permissions"])
