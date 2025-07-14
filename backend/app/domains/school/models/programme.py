from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import uuid4, UUID
from typing import List, Optional
from app.db.base_class import APIBase


class Programme(APIBase, table=True):
    __tablename__ = "programmes"

    name: str
    description: Optional[str] = None

    school_id: UUID = Field(foreign_key="schools.id")
    tenant_id: UUID = Field(foreign_key="public.tenants.id")

    classes: List["Class"] = Relationship(back_populates="programme")
    courses: List["Course"] = Relationship(back_populates="programme")
