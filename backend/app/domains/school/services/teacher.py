from typing import List

from fastapi import HTTPException, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.config.tenant_dependencies import get_tenant_id
from app.domains.school.models.teacher import Teacher
from app.domains.school.repository.teacher import TeacherRepository
from app.domains.school.repository.school import SchoolRepository
from app.domains.school.schemas import teacher as schemas
from app.utils.dependencies import get_tenant_session_dep


class TeacherService:
    def __init__(self, session: AsyncSession, tenant_id: UUID4):
        self.repo = TeacherRepository(session)
        self.tenant_id = tenant_id
        self.school_repo = SchoolRepository(session)

    async def create_teacher(
        self, 
        teacher_data: schemas.TeacherCreate,
        school_id: UUID4
    ) -> Teacher:
        """Create a new teacher for the current tenant"""
        school = await self.school_repo.get_by_id(school_id)
        if not school: raise HTTPException(status_code=404, detail="School not found")

        db_obj = await self.repo.create(dict(
            **teacher_data.model_dump(),
            school_id=school_id,
            tenant_id=self.tenant_id
        ))
        return db_obj
        
    async def get_teacher(self, teacher_id: UUID4) -> Teacher:
        """Get teacher details with tenant validation"""
        db_obj = await self.repo.get(teacher_id)
        if not db_obj: raise HTTPException(
            404, "Teacher not found"
        )
        return db_obj

    async def update_teacher(
            self,
            teacher_id: UUID4,
            update_data: schemas.TeacherUpdate
    ) -> Teacher:
        """Update teacher information"""
        db_obj = await self.repo.get(teacher_id)
        if not db_obj: raise HTTPException(
            404, "Teacher not found"
        )
        updated_teacher = await self.repo.update(
            db_obj=db_obj,
            obj_in=update_data.model_dump()
        )
        return updated_teacher

    async def list_teachers(
            self,
            skip: int = 0,
            limit: int = 100,
    ) -> List[Teacher]:
        """List all teachers for the tenant"""
        teachers = await self.repo.get_all(
            skip=skip,
            limit=limit
        )
        return teachers

    async def delete_teacher(
            self,
            teacher_id: UUID4
    ) -> None:
        """Delete a single teacher by id"""
        await self.repo.delete(teacher_id)


# Dependency for FastAPI
async def get_teacher_service(
        session: AsyncSession = Depends(get_tenant_session_dep),
        tenant_id: UUID4 = Depends(get_tenant_id)
):
    return TeacherService(session=session, tenant_id=tenant_id)

