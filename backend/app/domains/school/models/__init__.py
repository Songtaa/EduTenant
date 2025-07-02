from uuid import UUID
from sqlmodel import Field, Relationship
from app.domains.school.models.classes import Class
from app.domains.school.models.course import Course
from app.domains.school.models.parent import Parent
from app.domains.school.models.programme import Programme
from app.domains.school.models.school import School
from app.domains.school.models.services import Service
from app.domains.school.models.student import Student
from app.domains.school.models.teacher import Teacher
from app.domains.school.models.teacher_course import TeacherCourseLink
from app.domains.school.models.tenant import Tenant
from app.domains.school.models.tenant_role import TenantRole
from app.domains.school.models.tenant_role_permission import TenantRolePermission
from app.domains.school.models.tenant_user_permission import TenantUserPermission
from app.domains.school.models.tenant_user_role import TenantUserRole
from app.domains.auth.models.permission import Permission
from app.domains.auth.models.tenant_user import TenantUser
from app.domains.school.models.tenant_permission import TenantPermission


