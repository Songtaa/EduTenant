# app/schemas/school.py
from datetime import datetime
from uuid import UUID
from typing import Optional
from app.db.base_class import APIBase

class SchoolBase(APIBase):
    name: str
    address: str
    phone: str

class SchoolCreate(SchoolBase):
    pass

class SchoolUpdate(APIBase):
   
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

class SchoolOut(SchoolBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime  