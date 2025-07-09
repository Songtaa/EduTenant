# app/schemas/school.py
from datetime import datetime
from uuid import UUID
from typing import Optional
from app.db.base_class import APIBase

class SchoolBase(APIBase):
    name: str
    address: str
    phone: str
    contact_email: Optional[str] = None
    logo_url: Optional[str] = None
    established_year: Optional[int] = None

    tenant_id: Optional[UUID] = None


class SchoolCreate(SchoolBase):
    pass

class SchoolUpdate(APIBase):
   
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    contact_email: Optional[str] = None
    logo_url: Optional[str] = None
    established_year: Optional[int] = None

class SchoolOut(SchoolBase):
    id: UUID
    tenant_id: UUID
    created_date: datetime  