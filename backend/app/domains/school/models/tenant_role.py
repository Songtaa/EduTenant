from sqlmodel import SQLModel, Field, Relationship
from typing import List
from app.db.base_class import APIBase

from app.domains.school.models.tenant_permission import TenantPermission
from app.domains.school.models.tenant_role_permission import TenantRolePermission
from app.domains.school.models.tenant_user_role import TenantUserRole

class TenantRoleBase(APIBase):
    name: str = Field(max_length=50, unique=True, index=True)
    description: str | None = Field(default=None, max_length=200)
    is_system: bool = Field(default=False)

class TenantRole(TenantRoleBase, table=True):
    __tablename__ = "tenant_roles"
    
    
    permissions: List[TenantPermission] = Relationship(
        back_populates="roles",
        link_model=TenantRolePermission
    )
    users: List["User"] = Relationship(
        back_populates="tenant_roles",
        link_model=TenantUserRole
    )

    tenant_user_roles: List["TenantUserRole"] = Relationship(back_populates="role")

    
    