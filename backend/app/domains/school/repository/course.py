from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseRepository
from app.domains.school.models.course import Course
from app.domains.school.schemas.course import CourseCreate, CourseUpdate


class CourseRepository(BaseRepository[Course, CourseUpdate, CourseCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Course, session)
        
