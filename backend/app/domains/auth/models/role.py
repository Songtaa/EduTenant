from app.db.base_class import APIBase
from sqlalchemy import Column, String
from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4, UUID
from typing import List, Optional
from app.domains.auth.models.role_permission import RolePermission 
from app.domains.auth.models.user_role import UserRole



class Role(APIBase, table=True):
    __tablename__ = "roles"
    __table_args__ = {'schema': 'public'}

    id: UUID = Field(default_factory=uuid4, primary_key=True) 
    name: str = Field(index=True, unique=True, max_length=50)
    description: Optional[str] = Field(default=None, max_length=500)
   
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole, sa_relationship_kwargs={"viewonly": True})  
    permissions: List["Permission"] = Relationship(back_populates="roles", link_model=RolePermission, sa_relationship_kwargs={"viewonly": True})  
    role_permissions: List["RolePermission"] = Relationship(back_populates="role") 
    user_roles: List["UserRole"] = Relationship(back_populates="role")
