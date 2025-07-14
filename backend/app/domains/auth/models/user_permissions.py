from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from app.db.base_class import APIBase
from app.domains.auth.models.permission import Permission
from app.domains.auth.models.users import User


class UserPermission(APIBase, table=True):
    __tablename__ = "user_permissions"
    __table_args__ = {'schema': 'public'}

    user_id: UUID = Field(foreign_key="public.users.id", primary_key=True)
    permission_id: UUID = Field(foreign_key="public.permissions.id", primary_key=True)

    user: Optional["User"] = Relationship(back_populates="user_permissions")
    permission: Optional["Permission"] = Relationship(back_populates="permission_users")
