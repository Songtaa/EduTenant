from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseRepository
from app.domains.school.models.parent import Parent
from app.domains.school.schemas.parent import ParentCreate, ParentUpdate


class ParentRepository(BaseRepository[Parent, ParentUpdate, ParentCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Parent, session)
        
