from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Course(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    name: str
    description: str
    # teacher_id: Optional[UUID] = Field(default=None, foreign_key="teacher.id")
