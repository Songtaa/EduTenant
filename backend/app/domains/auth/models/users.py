from app.db.base_class import APIBase
from pydantic import EmailStr
from sqlalchemy import Column, String
from app.domains.auth.models.user_role import UserRole
from sqlmodel import Field, Relationship
from uuid import uuid4, UUID
from typing import List
from app.domains.school.models.tenant_role import TenantUserRole
from app.domains.school.models.tenant_role import TenantRole


class User(APIBase, table=True):
    __tablename__ = "users"
    __table_args__ = {'schema': 'public'}

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(sa_column=Column(String(255), nullable=False, unique=True))
    password: str = Field(nullable=False, max_length=255)
    is_active: bool = Field(default=True)
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    
    # role: List["Role"] = Relationship(back_populates="users", link_model=UserRole)

    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRole, sa_relationship_kwargs={"viewonly": True})
    user_roles: List["UserRole"] = Relationship(back_populates="user") 
    user_permissions: List["UserPermission"] = Relationship(back_populates='user')
    tenant_roles: List["TenantRole"] = Relationship(back_populates="users", link_model=TenantUserRole, sa_relationship_kwargs={"viewonly": True})
    tenant_user_roles: List["TenantUserRole"] = Relationship(back_populates="user")
    tokens: List["TokenBlocklist"] = Relationship(back_populates="user")

