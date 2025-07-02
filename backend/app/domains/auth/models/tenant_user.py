# app/domains/auth/models/tenant_user.py
from uuid import UUID, uuid4
from typing import List, Optional
from app.domains.auth.models.user_permissions import UserPermission
from sqlmodel import SQLModel, Field, Relationship, Column, String
from pydantic import EmailStr

from app.domains.auth.models.permission import Permission

from app.domains.school.models.tenant_role import TenantUserRole
from app.domains.school.models.tenant_role import TenantRole
from app.db.base_class import APIBase


class TenantUser(APIBase, table=True):
    __tablename__ = "tenant_users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(sa_column=Column(String(255), nullable=False, unique=True))
    password: str = Field(nullable=False, max_length=255)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    full_name: Optional[str] = Field(default=None, max_length=255)

    tenant_roles: List["TenantRole"] = Relationship(
        back_populates="users", 
        link_model=TenantUserRole, 
        sa_relationship_kwargs={"viewonly": True}
    )

    tenant_user_permissions: List["TenantUserPermission"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[TenantUserPermission.user_id]"}
    )
    tenant_user_roles: List["TenantUserRole"] = Relationship(back_populates="user")
