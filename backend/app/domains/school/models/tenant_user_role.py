from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship
from typing import List
from app.db.base_class import APIBase
from typing import Optional

class TenantUserRole(APIBase, table=True):
    __tablename__ = "tenant_user_roles"
    
    
    user_id: UUID = Field(
        foreign_key="public.users.id",
        primary_key=True
    )
    role_id: UUID = Field(
        foreign_key="tenant_roles.id",
        primary_key=True
    )

    user: Optional["User"] = Relationship(back_populates="tenant_user_roles")
    role: Optional["TenantRole"] = Relationship(back_populates="tenant_user_roles")
    # assigned_by: UUID | None = Field(
    #     foreign_key="public.users.id",
    #     default=None
    # )
    