from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from app.db.base_class import APIBase


class TenantUserPermissionBase(APIBase):
    expires_at: Optional[datetime] = None
    

class TenantUserPermission(TenantUserPermissionBase, table=True):
    __tablename__ = "tenant_user_permissions"
    
    
    user_id: UUID = Field(
        foreign_key="tenant_users.id",
        primary_key=True
    )
    permission_id: UUID = Field(
        foreign_key="public.tenant_permissions.id",
        primary_key=True
    )
    
    # Relationship to permission (many-to-one)
    permission: "TenantPermission" = Relationship(back_populates="direct_user_assignments")
    user: Optional["TenantUser"] = Relationship(
        back_populates="tenant_user_permissions",
        sa_relationship_kwargs={"foreign_keys": "[TenantUserPermission.user_id]"}
    )

    
   