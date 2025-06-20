from sqlmodel import SQLModel, Field, Relationship
from typing import List
from app.domains.school.models.tenant_role_permission import TenantRolePermission
from app.db.base_class import APIBase


class TenantPermissionBase(APIBase):
    name: str = Field(max_length=100, unique=True, index=True)
    description: str | None = Field(default=None, max_length=200)

class TenantPermission(TenantPermissionBase, table=True):
    __tablename__ = "tenant_permissions"
    __table_args__ = {"schema": "public"}  
    
    # Relationships
    roles: List["TenantRole"] = Relationship(
        back_populates="permissions",
        link_model=TenantRolePermission
    )
    direct_user_assignments: List["TenantUserPermission"] = Relationship(
        back_populates="permission"
    )