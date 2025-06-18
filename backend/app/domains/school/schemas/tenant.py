# app/schemas/tenant.py
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.db.base_class import APIBase

class TenantBase(APIBase):
    schema_name: str
    subdomain: str
    is_active: bool
    billing_tier: str

class TenantCreate(TenantBase):
    pass

class TenantUpdate(APIBase):
   
    name: Optional[str] = None
    subdomain: Optional[str] = None
    is_active: Optional[bool] = None
    billing_tier: Optional[str] = None

class TenantRead(TenantBase):
    id: UUID
    
    class Config:
        orm_mode = True


class TenantSchema(TenantRead):
    pass