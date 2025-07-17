from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseRepository
from app.domains.school.models.student import Student
from app.domains.school.schemas.student import StudentCreate, StudentUpdate


class StudentRepository(BaseRepository[Student, StudentUpdate, StudentCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Student, session)
        
