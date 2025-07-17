from fastapi import APIRouter, Depends

from app.domains.school.apis.classes import class_router
from app.domains.school.apis.course import course_router
from app.domains.school.apis.parent import parent_router
from app.domains.school.apis.programme import programme_router
# from app.domains.auth.apis.users_router import user_router
# from app.domains.auth.apis.role import role_router
# from app.domains.auth.apis.permission import permission_router
from app.domains.school.apis.services_router import service_router
from app.domains.school.apis.school import school_router
from app.config.tenant_dependencies import require_tenant_context
from app.domains.school.apis.student import student_router
from app.domains.school.apis.teacher import teacher_router

tenant_router = APIRouter(dependencies=[Depends(require_tenant_context)])
# tenant_router.include_router(user_router, prefix="/users", tags=["Users"])
# tenant_router.include_router(role_router, prefix="/roles", tags=["Roles"])
# tenant_router.include_router(permission_router, prefix="/permissions", tags=["Permissions"])
tenant_router.include_router(service_router, prefix="/services", tags=["Services"])
tenant_router.include_router(school_router, prefix="/schools", tags=["Schools"])
tenant_router.include_router(class_router, prefix="/schools/{school_id}", tags=["Classes"])
tenant_router.include_router(course_router, prefix="/schools/{school_id}", tags=["Courses"])
tenant_router.include_router(parent_router, prefix="/schools/{school_id}", tags=["Parents"])
tenant_router.include_router(programme_router, prefix="/schools/{school_id}", tags=["Programmes"])
tenant_router.include_router(student_router, prefix="/schools/{school_id}", tags=["Students"])
tenant_router.include_router(teacher_router, prefix="/schools/{school_id}", tags=["Teachers"])
