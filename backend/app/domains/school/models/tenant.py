# app/models/tenant.py
from sqlalchemy import Column, String, Boolean, DateTime

from app.db.base_class import APIBase

from datetime import datetime
from sqlmodel import Field, Relationship
from typing import List
from app.domains.school.models.school import School
# from app.models.base import APIBase

class Tenant(APIBase, table=True):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "public"}
    
    schema_name: str = Field(max_length=255, index=True)
    subdomain: str = Field(max_length=255, unique=True)
    is_active: bool = Field(default=True)
    billing_tier: str = Field(max_length=50, default="basic")
    
    # Relationship to cached school data (optional)
    schools: List["School"] = Relationship(back_populates="tenant")




