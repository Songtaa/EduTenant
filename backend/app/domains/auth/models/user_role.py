from app.db.base_class import APIBase
from pydantic import EmailStr
from sqlalchemy import Column, String
from sqlmodel import Field, Relationship
from uuid import uuid4, UUID
from typing import List, Optional



class UserRole(APIBase, table=True):
    __tablename__ = "user_roles"
    __table_args__ = {"schema": "public"}

    user_id: UUID = Field(foreign_key="public.users.id", primary_key=True)
    role_id: UUID = Field(foreign_key="public.roles.id", primary_key=True)

    # role: Optional["Role"] = Relationship(back_populates="roles")
    # user: Optional["User"] = Relationship(back_populates="users")

    role: Optional["Role"] = Relationship(back_populates="user_roles")
    user: Optional["User"] = Relationship(back_populates="user_roles")