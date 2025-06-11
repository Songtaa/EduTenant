from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, ForeignKey
from app.db.base_class import APIBase
from sqlmodel import Field, Relationship




class TeacherCourseLink(APIBase, table=True):
    __tablename__ = "teachercourselinks"

    teacher_id: UUID = Field(foreign_key="teacher.id", primary_key=True)
    course_id: UUID = Field(foreign_key="course.id", primary_key=True)