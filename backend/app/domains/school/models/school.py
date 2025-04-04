# app/models/school.py
from uuid import UUID
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import APIBase
from sqlmodel import Field, Relationship
from typing import List, Optional
from app.db.base_class import APIBase
from app.domains.school.models.tenant import Tenant
from app.domains.school.models.student import Student

class School(APIBase, table=True):
    __tablename__ = "schools"
    
    name: str = Field(max_length=255)
    address: str = Field(max_length=500)
    phone: str = Field(max_length=50)
    tenant_id: Optional[UUID] = Field(index=True) 

    # Relationships
    students: List["Student"] = Relationship(back_populates="school")
    tenant: "Tenant" = Relationship(back_populates="schools")