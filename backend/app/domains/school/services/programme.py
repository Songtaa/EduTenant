from typing import List

from fastapi import HTTPException, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.config.tenant_dependencies import get_tenant_id
from app.domains.school.models.programme import Programme
from app.domains.school.repository.programme import ProgrammeRepository
from app.domains.school.repository.school import SchoolRepository
from app.domains.school.schemas import programme as schemas
from app.utils.dependencies import get_tenant_session_dep


class ProgrammeService:
    def __init__(self, session: AsyncSession, tenant_id: UUID4):
        self.repo = ProgrammeRepository(session)
        self.tenant_id = tenant_id
        self.school_repo = SchoolRepository(session)

    async def create_programme(
        self, 
        programme_data: schemas.ProgrammeCreate,
        school_id: UUID4
    ) -> Programme:
        """Create a new programme for the current tenant"""
        school = await self.school_repo.get_by_id(school_id)
        if not school: raise HTTPException(status_code=404, detail="School not found")

        db_obj = await self.repo.create(dict(
            **programme_data.model_dump(),
            school_id=school_id,
            tenant_id=self.tenant_id
        ))
        return db_obj
        
    async def get_programme(self, programme_id: UUID4) -> Programme:
        """Get programme details with tenant validation"""
        db_obj = await self.repo.get(programme_id)
        if not db_obj: raise HTTPException(
            404, "Programme not found"
        )
        return db_obj

    async def update_programme(
            self,
            programme_id: UUID4,
            update_data: schemas.ProgrammeUpdate
    ) -> Programme:
        """Update programme information"""
        db_obj = await self.repo.get(programme_id)
        if not db_obj: raise HTTPException(
            404, "Programme not found"
        )
        updated_programme = await self.repo.update(
            db_obj=db_obj,
            obj_in=update_data.model_dump()
        )
        return updated_programme

    async def list_programmes(
            self,
            skip: int = 0,
            limit: int = 100,
    ) -> List[Programme]:
        """List all programmes for the tenant"""
        programmes = await self.repo.get_all(
            skip=skip,
            limit=limit
        )
        return programmes

    async def delete_programme(
            self,
            programme_id: UUID4
    ) -> None:
        """Delete a single programme by id"""
        await self.repo.delete(programme_id)


# Dependency for FastAPI
async def get_programme_service(
        session: AsyncSession = Depends(get_tenant_session_dep),
        tenant_id: UUID4 = Depends(get_tenant_id)
):
    return ProgrammeService(session=session, tenant_id=tenant_id)

