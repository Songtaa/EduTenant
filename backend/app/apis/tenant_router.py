from fastapi import APIRouter, Depends
from app.domains.auth.apis.users_router import user_router
from app.domains.auth.apis.role import role_router
from app.domains.auth.apis.permission import permission_router
from app.domains.school.apis.services_router import service_router
from app.domains.school.apis.school import school_router
from app.config.tenant_dependencies import require_tenant_context

tenant_router = APIRouter(dependencies=[Depends(require_tenant_context)])
tenant_router.include_router(user_router, prefix="/users", tags=["Users"])
tenant_router.include_router(role_router, prefix="/roles", tags=["Roles"])
tenant_router.include_router(permission_router, prefix="/permissions", tags=["Permissions"])
tenant_router.include_router(service_router, prefix="/services", tags=["Services"])
tenant_router.include_router(school_router, prefix="/schools", tags=["Schools"])
