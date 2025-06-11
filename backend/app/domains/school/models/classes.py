from app.domains.school.models.student import Student
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import uuid4, UUID
from typing import List, Optional
from app.db.base_class import APIBase


class Class(APIBase, table=True):
    __tablename__ = "classes"
    
    name: str
    year: int
    programme_id: UUID = Field(foreign_key="programme.id")

    programme: Optional["Programme"] = Relationship(back_populates="classes")
    students: List["Student"] = Relationship(back_populates="class_")

