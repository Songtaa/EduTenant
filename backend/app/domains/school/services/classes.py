from typing import List

from fastapi import HTTPException, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.config.tenant_dependencies import get_tenant_id
from app.domains.school.models.classes import Class
from app.domains.school.repository.classes import ClassesRepository
from app.domains.school.repository.school import SchoolRepository
from app.domains.school.schemas import classes as schemas
from app.utils.dependencies import get_tenant_session_dep


class ClassService:
    def __init__(self, session: AsyncSession, tenant_id: UUID4):
        self.repo = ClassesRepository(session)
        self.tenant_id = tenant_id
        self.school_repo = SchoolRepository(session)

    async def create_class(self, class_data: schemas.ClassesCreate, school_id: UUID4) -> Class:
        """Create a new class for the current tenant"""
        school = await self.school_repo.get_by_id(school_id)
        if not school: raise HTTPException(status_code=404, detail="School not found")

        db_obj = await self.repo.create(dict(
            **class_data.model_dump(),
            school_id=school_id,
            tenant_id=self.tenant_id
        ))
        return db_obj

    async def get_class(self, class_id: UUID4) -> Class:
        """Get class details with tenant validation"""
        db_obj = await self.repo.get(class_id)
        if not db_obj: raise HTTPException(
            404, "class not found"
        )
        return db_obj

    async def update_class(
            self,
            class_id: UUID4,
            update_data: schemas.ClassesUpdate
    ) -> Class:
        """Update class information"""
        db_obj = await self.repo.get(class_id)
        if not db_obj: raise HTTPException(
            404, "Class not found"
        )
        updated_class = await self.repo.update(
            db_obj=db_obj,
            obj_in=update_data.model_dump()
        )
        return updated_class

    async def list_classes(
            self,
            skip: int = 0,
            limit: int = 100
    ) -> List[Class]:
        """List all classes for the tenant"""
        classes = await self.repo.get_all(
            skip=skip,
            limit=limit
        )
        return classes

    async def delete_class(
            self,
            class_id: UUID4
    ) -> None:
        """List all classes for the tenant"""
        await self.repo.delete(class_id)


# Dependency for FastAPI
async def get_class_service(
        session: AsyncSession = Depends(get_tenant_session_dep),
        tenant_id: UUID4 = Depends(get_tenant_id)
):
    return ClassService(session=session, tenant_id=tenant_id)
