from typing import List

from fastapi import HTTPException, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.config.tenant_dependencies import get_tenant_id
from app.domains.school.models.course import Course
from app.domains.school.repository.course import CourseRepository
from app.domains.school.repository.school import SchoolRepository
from app.domains.school.schemas import course as schemas
from app.utils.dependencies import get_tenant_session_dep


class CourseService:
    def __init__(self, session: AsyncSession, tenant_id: UUID4):
        self.repo = CourseRepository(session)
        self.tenant_id = tenant_id
        self.school_repo = SchoolRepository(session)

    async def create_course(
        self, 
        course_data: schemas.CourseCreate,
        school_id: UUID4
    ) -> Course:
        """Create a new course for the current tenant"""
        school = await self.school_repo.get_by_id(school_id)
        if not school: raise HTTPException(status_code=404, detail="School not found")

        db_obj = await self.repo.create(dict(
            **course_data.model_dump(),
            school_id=school_id,
            tenant_id=self.tenant_id
        ))
        return db_obj
        
    async def get_course(self, course_id: UUID4) -> Course:
        """Get course details with tenant validation"""
        db_obj = await self.repo.get(course_id)
        if not db_obj: raise HTTPException(
            404, "Course not found"
        )
        return db_obj

    async def update_course(
            self,
            course_id: UUID4,
            update_data: schemas.CourseUpdate
    ) -> Course:
        """Update course information"""
        db_obj = await self.repo.get(course_id)
        if not db_obj: raise HTTPException(
            404, "Course not found"
        )
        updated_course = await self.repo.update(
            db_obj=db_obj,
            obj_in=update_data.model_dump()
        )
        return updated_course

    async def list_courses(
            self,
            skip: int = 0,
            limit: int = 100,
    ) -> List[Course]:
        """List all courses for the tenant"""
        courses = await self.repo.get_all(
            skip=skip,
            limit=limit
        )
        return courses

    async def delete_course(
            self,
            course_id: UUID4
    ) -> None:
        """Delete a single course by id"""
        await self.repo.delete(course_id)


# Dependency for FastAPI
async def get_course_service(
        session: AsyncSession = Depends(get_tenant_session_dep),
        tenant_id: UUID4 = Depends(get_tenant_id)
):
    return CourseService(session=session, tenant_id=tenant_id)

