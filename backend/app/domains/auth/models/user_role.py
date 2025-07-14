from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from app.db.base_class import APIBase


class UserRole(APIBase, table=True):
    __tablename__ = "user_roles"
    __table_args__ = {'schema': 'public'}

    user_id: UUID = Field(foreign_key="public.users.id", primary_key=True)
    role_id: UUID = Field(foreign_key="public.roles.id", primary_key=True)

    tenant_id: Optional[UUID] = Field(default=None)
    __tablename__ = "user_roles"
    __table_args__ = {"schema": "public"}

    role: Optional["Role"] = Relationship(back_populates="user_roles")
    user: Optional["User"] = Relationship(back_populates="user_roles")
