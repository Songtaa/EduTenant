from app.db.base_class import APIBase
from pydantic import EmailStr
from sqlalchemy import Column, String
from app.domains.auth.models.user_role import UserRole
from sqlmodel import Field, Relationship
from uuid import uuid4, UUID
from typing import List


class UserTenant(APIBase, table=True):
    __tablename__ = "user_tenants"
    __table_args__ = {"schema": "public"}
    
    user_id: int = Field(foreign_key="public.users.id", primary_key=True)
    tenant_id: int = Field(foreign_key="public.tenants.id", primary_key=True)
    is_admin: bool = Field(default=False)