# from domains.kace.apis.attendance import attendance_router
# from domains.kace.apis.class_student import class_student_router
# from domains.kace.apis.class_teacher import class_teacher_router
# from domains.kace.apis.courseclass import courseclass_router
# from domains.kace.apis.courses import course_router
# from domains.kace.apis.grades import grade_router
# from domains.kace.apis.messages import message_router
# from domains.kace.apis.module_tutor import module_tutor_router
# from domains.kace.apis.modules import module_router
# from domains.kace.apis.notifications import notification_router
# from domains.kace.apis.parent import parent_router
# from domains.kace.apis.profiles import profiles_router
from app.domains.auth.apis.users_router import user_router
from app.domains.auth.apis.login_router import auth_router
from app.domains.school.apis.services_router import service_router
from app.domains.auth.apis.role import role_router
from app.domains.auth.apis.permission import permission_router
from app.domains.school.apis.tenant import tenant_router
from app.domains.school.apis.school import school_router
from fastapi import APIRouter

router = APIRouter()
# router.include_router(attendance_router)
# router.include_router(class_student_router)
# router.include_router(class_teacher_router)
# router.include_router(course_router)
# router.include_router(courseclass_router)
# router.include_router(grade_router)
# router.include_router(message_router)
# router.include_router(module_router)
# router.include_router(module_tutor_router)
# router.include_router(notification_router)
# router.include_router(parent_router)
# router.include_router(profiles_router)
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(service_router)
router.include_router(role_router)
router.include_router(permission_router)
router.include_router(tenant_router)
router.include_router(school_router)
