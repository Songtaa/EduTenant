# app/repositories/school.py
from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from app.domains.school.models.school import School
from app.crud.base import BaseRepository
from app.domains.school.schemas.school import SchoolCreate, SchoolOut, SchoolUpdate
from sqlmodel.ext.asyncio.session import AsyncSession


class SchoolRepository(BaseRepository[School, SchoolUpdate, SchoolCreate]):
    def __init__(self, session: AsyncSession):
        super().__init__(School, session)

    async def get_by_name_and_tenant(self, name: str, tenant_id: UUID) -> Optional[SchoolOut]:
        result = await self.session.execute(
            select(School)
            .where(School.name == name)
            .where(School.tenant_id == tenant_id)
        )
        school = result.scalars().first()
        return SchoolOut.from_orm(school) if school else None

    async def get_all(
        self,
        tenant_id: UUID,
        search_term: Optional[str] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[SchoolOut]:
        query = select(School).where(School.tenant_id == tenant_id)
        
        # if active_only:
        #     query = query.where(School.is_active == True)
            
        if search_term:
            query = query.where(School.name.ilike(f"%{search_term}%"))
            
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        schools = result.scalars().all()
        return [SchoolOut.from_orm(s) for s in schools]

    async def update(self, school_id: UUID, update_data: dict) -> Optional[SchoolOut]:
        school = await self.get_by_id(school_id)
        if not school:
            return None
            
        for key, value in update_data.items():
            setattr(school, key, value)
            
        self.session.add(school)
        await self.session.commit()
        await self.session.refresh(school)
        return SchoolOut.from_orm(school)


    def get_main_school(self, tenant_id: UUID) -> Optional[School]:
        return self.session.exec(
            select(School)
            .where(School.tenant_id == tenant_id)
            .where(School.name == "Main Campus")
        ).first()