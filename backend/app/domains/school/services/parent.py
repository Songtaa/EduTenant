from typing import List

from fastapi import HTTPException, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.config.tenant_dependencies import get_tenant_id
from app.domains.school.models.parent import Parent
from app.domains.school.repository.parent import ParentRepository
from app.domains.school.repository.school import SchoolRepository
from app.domains.school.schemas import parent as schemas
from app.utils.dependencies import get_tenant_session_dep


class ParentService:
    def __init__(self, session: AsyncSession, tenant_id: UUID4):
        self.repo = ParentRepository(session)
        self.tenant_id = tenant_id
        self.school_repo = SchoolRepository(session)

    async def create_parent(
        self, 
        parent_data: schemas.ParentCreate,
        school_id: UUID4
    ) -> Parent:
        """Create a new parent for the current tenant"""
        school = await self.school_repo.get_by_id(school_id)
        if not school: raise HTTPException(status_code=404, detail="School not found")

        db_obj = await self.repo.create(dict(
            **parent_data.model_dump(),
            school_id=school_id,
            tenant_id=self.tenant_id
        ))
        return db_obj
        
    async def get_parent(self, parent_id: UUID4) -> Parent:
        """Get parent details with tenant validation"""
        db_obj = await self.repo.get(parent_id)
        if not db_obj: raise HTTPException(
            404, "Parent not found"
        )
        return db_obj

    async def update_parent(
            self,
            parent_id: UUID4,
            update_data: schemas.ParentUpdate
    ) -> Parent:
        """Update parent information"""
        db_obj = await self.repo.get(parent_id)
        if not db_obj: raise HTTPException(
            404, "Parent not found"
        )
        updated_parent = await self.repo.update(
            db_obj=db_obj,
            obj_in=update_data.model_dump()
        )
        return updated_parent

    async def list_parents(
            self,
            skip: int = 0,
            limit: int = 100,
    ) -> List[Parent]:
        """List all parents for the tenant"""
        parents = await self.repo.get_all(
            skip=skip,
            limit=limit
        )
        return parents

    async def delete_parent(
            self,
            parent_id: UUID4
    ) -> None:
        """Delete a single parent by id"""
        await self.repo.delete(parent_id)


# Dependency for FastAPI
async def get_parent_service(
        session: AsyncSession = Depends(get_tenant_session_dep),
        tenant_id: UUID4 = Depends(get_tenant_id)
):
    return ParentService(session=session, tenant_id=tenant_id)

