from app.db.base_class import APIBase
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID
from typing import Optional

class RolePermission(APIBase, table=True):
    role_id: UUID = Field(foreign_key="roles.id", primary_key=True)
    permission_id: UUID = Field(foreign_key="permissions.id")
    
    # role: Optional["Role"] = Relationship(back_populates="role_permissions")
    # permission: Optional["Permission"] = Relationship(back_populates="permission_roles")

    role: Optional["Role"] = Relationship(back_populates="role_permissions") 
    permission: Optional["Permission"] = Relationship(back_populates="role_permissions")



