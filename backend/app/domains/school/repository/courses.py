from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List
from app.domains.kace.models.courses import Course

class CourseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_courses(self) -> List[Course]:
        statement = select(Course)
        result = await self.session.exec(statement)
        return result.scalars().all()