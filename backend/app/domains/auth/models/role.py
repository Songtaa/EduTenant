from app.db.base_class import APIBase
from sqlalchemy import Column, String
from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4, UUID
from typing import List
from app.domains.auth.models.role_permission import RolePermission 
from app.domains.auth.models.user_role import UserRole



class Role(APIBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True) 
    name: str = Field(index=True)
    # users: List["User"] = Relationship(back_populates="roles", link_model=UserRole)
    # permissions: List["Permission"] = Relationship(back_populates="role", link_model=RolePermission)
    # role_permissions: List["RolePermission"] = Relationship(back_populates="role")
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole, sa_relationship_kwargs={"viewonly": True})  
    permissions: List["Permission"] = Relationship(back_populates="roles", link_model=RolePermission, sa_relationship_kwargs={"viewonly": True})  
    role_permissions: List["RolePermission"] = Relationship(back_populates="role") 
    user_roles: List["UserRole"] = Relationship(back_populates="role")
