from app.domains.auth.models.role_permission import RolePermission
from app.db.base_class import APIBase
from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4, UUID
from typing import List, Optional


class Permission(APIBase, table=True):

    __tablename__ = "permissions"
    __table_args__ = {'schema': 'public'}
    
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None, max_length=500)

    roles: List["Role"] = Relationship(back_populates="permissions", link_model=RolePermission, sa_relationship_kwargs={"viewonly": True})
    role_permissions: List["RolePermission"] = Relationship(back_populates="permission")
    permission_users: List["UserPermission"]= Relationship( back_populates="permission")