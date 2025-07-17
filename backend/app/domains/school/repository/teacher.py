from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseRepository
from app.domains.school.models.teacher import Teacher
from app.domains.school.schemas.teacher import TeacherCreate, TeacherUpdate


class TeacherRepository(BaseRepository[Teacher, TeacherUpdate, TeacherCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Teacher, session)
        
