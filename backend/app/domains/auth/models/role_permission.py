from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from app.db.base_class import APIBase


class RolePermission(APIBase, table=True):
    __tablename__ = "role_permissions"
    __table_args__ = {'schema': 'public'}

    role_id: UUID = Field(foreign_key="public.roles.id", primary_key=True)
    permission_id: UUID = Field(foreign_key="public.permissions.id", primary_key=True)

    role: Optional["Role"] = Relationship(back_populates="role_permissions")
    permission: Optional["Permission"] = Relationship(back_populates="role_permissions")
