from uuid import UUID
from app.domains.auth.models.permission import Permission
from app.domains.auth.models.users import User
from sqlmodel import Field, Relationship
from typing import Optional
from app.db.base_class import APIBase


class UserPermission(APIBase, table=True):
    
    user_id: UUID = Field(foreign_key="public.users.id", primary_key=True)
    permission_id: UUID = Field(foreign_key="public.permissions.id", primary_key=True)

    user: Optional["User"] = Relationship(back_populates="user_permissions")
    permission: Optional["Permission"] = Relationship(back_populates="permission_users")