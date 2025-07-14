from uuid import UUID

from sqlmodel import Field

from app.db.base_class import APIBase


class TeacherCourseLink(APIBase, table=True):
    __tablename__ = "teachercourselinks"

    teacher_id: UUID = Field(foreign_key="teachers.id", primary_key=True)
    course_id: UUID = Field(foreign_key="courses.id", primary_key=True)
