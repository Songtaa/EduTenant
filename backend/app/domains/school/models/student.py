
# app/models/school.py
from uuid import UUID
from sqlalchemy import Column, String, ForeignKey
from app.db.base_class import APIBase
from sqlmodel import Field, Relationship
from app.db.base_class import APIBase
from app.domains.school.models.school import School


class Student(APIBase, table=True):
    __tablename__ = "students"
    
    full_name: str = Field(max_length=255, index=True)
    email: str = Field(max_length=255, unique=True)
    grade_level: str = Field(max_length=50)
    school_id: UUID = Field(foreign_key="schools.id")
    
    # Relationships
    school: "School" = Relationship(back_populates="students")
