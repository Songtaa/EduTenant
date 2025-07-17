from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseRepository
from app.domains.school.models.classes import Class
from app.domains.school.schemas import classes as schema


class ClassesRepository(BaseRepository[Class, schema.ClassesCreate, schema.ClassesUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Class, session)
