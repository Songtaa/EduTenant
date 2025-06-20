from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from app.db.base_class import APIBase


class TenantUserPermissionBase(APIBase):
    expires_at: Optional[datetime] = None
    granted_by: Optional[UUID] = Field(
        foreign_key="public.users.id",
        default=None
    )

class TenantUserPermission(TenantUserPermissionBase, table=True):
    __tablename__ = "tenant_user_permissions"
    
    
    user_id: UUID = Field(
        foreign_key="public.users.id",
        primary_key=True
    )
    permission_id: UUID = Field(
        foreign_key="public.tenant_permissions.id",
        primary_key=True
    )
    
    # Relationship to permission (many-to-one)
    permission: "TenantPermission" = Relationship(back_populates="direct_user_assignments")
    
   