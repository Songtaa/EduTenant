from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseRepository
from app.domains.school.models.programme import Programme
from app.domains.school.schemas.programme import ProgrammeCreate, ProgrammeUpdate


class ProgrammeRepository(BaseRepository[Programme, ProgrammeUpdate, ProgrammeCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Programme, session)
        
