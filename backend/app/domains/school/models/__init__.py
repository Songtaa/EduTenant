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


# from typing import Dict, Type
# from app.db.base_class import APIBase


# def create_tenant_rbac_models(tenant_schema: str) -> Dict[str, Type[APIBase]]:
#     """Dynamically creates tenant-specific RBAC models with proper schema bindings"""
    
#     # First define the permission model (public schema)
#     class DynamicTenantPermission(TenantPermission):
#         __table_args__ = ({'schema': 'public'},)
        
#     # Then define tenant-specific models with proper FK references
#     class DynamicTenantRole(TenantRole, table=True):
#         __tablename__ = "tenant_roles"
#         __table_args__ = ({'schema': tenant_schema},)
        
#         id: UUID = Field(primary_key=True)
#         permissions: list["DynamicTenantPermission"] = Relationship(
#             back_populates="tenant_roles",
#             link_model="DynamicTenantRolePermission"
#         )

#     class DynamicTenantRolePermission(TenantRolePermission, table=True):
#         __tablename__ = "tenant_role_permissions"
#         __table_args__ = ({'schema': tenant_schema},)
        
#         role_id: UUID = Field(
#             foreign_key=f"{tenant_schema}.roles.id",
#             primary_key=True
#         )
#         permission_id: UUID = Field(
#             foreign_key="public.permissions.id",
#             primary_key=True
#         )

#     class DynamicTenantUserRole(TenantUserRole, table=True):
#         __tablename__ = "tenant_user_roles"
#         __table_args__ = ({'schema': tenant_schema},)
        
#         user_id: UUID = Field(
#             foreign_key="public.users.id",
#             primary_key=True
#         )
#         role_id: UUID = Field(
#             foreign_key=f"{tenant_schema}.roles.id",
#             primary_key=True
#         )

#     class DynamicTenantUserPermission(TenantUserPermission, table=True):
#         __tablename__ = "tenant_user_permissions"
#         __table_args__ = ({'schema': tenant_schema},)
        
#         permission_id: UUID = Field(
#             foreign_key="public.permissions.id",
#             primary_key=True
#         )
#         user_id: UUID = Field(
#             foreign_key="public.users.id",
#             primary_key=True
#         )

#     # Update forward references
#     DynamicTenantRole.update_forward_refs()
#     DynamicTenantPermission.update_forward_refs()

#     return {
#         "TenantRole": DynamicTenantRole,
#         "TenantPermission": DynamicTenantPermission,
#         "TenantRolePermission": DynamicTenantRolePermission,
#         "TenantUserRole": DynamicTenantUserRole,
#         "TenantUserPermission": DynamicTenantUserPermission
#     }