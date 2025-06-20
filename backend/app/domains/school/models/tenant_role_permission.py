from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship
from typing import List
from app.db.base_class import APIBase

class TenantRolePermission(APIBase, table=True):
    __tablename__ = "tenant_role_permissions"
    

    role_id: UUID = Field(
        foreign_key="tenant_roles.id",
        primary_key=True
    )
    permission_id: UUID = Field(
        foreign_key="public.tenant_permissions.id",
        primary_key=True
    )
 