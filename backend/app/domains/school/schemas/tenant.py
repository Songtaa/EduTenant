# app/schemas/tenant.py
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.db.base_class import APIBase
from pydantic import UUID4, ConfigDict, EmailStr, Field
from sqlmodel import SQLModel



class TenantBase(SQLModel):
    schema_name: str
    subdomain: str
    is_active: bool
    billing_tier: str

class TenantCreate(TenantBase):
    pass

class TenantUpdate(TenantBase):
   
    schema_name: Optional[str] = None
    subdomain: Optional[str] = None
    is_active: Optional[bool] = None
    billing_tier: Optional[str] = None

class TenantRead(TenantBase):
    id: UUID
    
    model_config = ConfigDict(from_attributes=True)


class TenantSchema(TenantRead):
    pass