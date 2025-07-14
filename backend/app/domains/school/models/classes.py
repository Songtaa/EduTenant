from typing import List, Optional
from uuid import UUID

from sqlmodel import Field, Relationship

from app.db.base_class import APIBase
from app.domains.school.models.student import Student


class Class(APIBase, table=True):
    __tablename__ = "classes"

    name: str
    academic_year: int
    programme_id: UUID = Field(foreign_key="programmes.id")
    school_id: UUID = Field(foreign_key="schools.id")

    tenant_id: UUID = Field(foreign_key="public.tenants.id")

    school: Optional["School"] = Relationship(back_populates="classes")
    programme: Optional["Programme"] = Relationship(back_populates="classes")
    students: List["Student"] = Relationship(back_populates="class_")
