from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import Column, String, ForeignKey
from app.db.base_class import APIBase
from sqlmodel import Field, Relationship



class Student(APIBase, table=True):
    __tablename__ = "students"
    
    full_name: str = Field(max_length=255, index=True)
    email: str = Field(max_length=255, unique=True)
    date_of_birth: Optional[datetime] = None
    class_id: Optional[UUID] = Field(foreign_key="classes.id")


    parent_id: Optional[UUID] = Field(foreign_key="parents.id")
    class_: Optional["Class"] = Relationship(back_populates="students")
