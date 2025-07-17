from typing import List

from fastapi import HTTPException, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.config.tenant_dependencies import get_tenant_id
from app.domains.school.models.student import Student
from app.domains.school.repository.student import StudentRepository
from app.domains.school.repository.school import SchoolRepository
from app.domains.school.schemas import student as schemas
from app.utils.dependencies import get_tenant_session_dep


class StudentService:
    def __init__(self, session: AsyncSession, tenant_id: UUID4):
        self.repo = StudentRepository(session)
        self.tenant_id = tenant_id
        self.school_repo = SchoolRepository(session)

    async def create_student(
        self, 
        student_data: schemas.StudentCreate,
        school_id: UUID4
    ) -> Student:
        """Create a new student for the current tenant"""
        school = await self.school_repo.get_by_id(school_id)
        if not school: raise HTTPException(status_code=404, detail="School not found")

        db_obj = await self.repo.create(dict(
            **student_data.model_dump(),
            school_id=school_id,
            tenant_id=self.tenant_id
        ))
        return db_obj
        
    async def get_student(self, student_id: UUID4) -> Student:
        """Get student details with tenant validation"""
        db_obj = await self.repo.get(student_id)
        if not db_obj: raise HTTPException(
            404, "Student not found"
        )
        return db_obj

    async def update_student(
            self,
            student_id: UUID4,
            update_data: schemas.StudentUpdate
    ) -> Student:
        """Update student information"""
        db_obj = await self.repo.get(student_id)
        if not db_obj: raise HTTPException(
            404, "Student not found"
        )
        updated_student = await self.repo.update(
            db_obj=db_obj,
            obj_in=update_data.model_dump()
        )
        return updated_student

    async def list_students(
            self,
            skip: int = 0,
            limit: int = 100,
    ) -> List[Student]:
        """List all students for the tenant"""
        students = await self.repo.get_all(
            skip=skip,
            limit=limit
        )
        return students

    async def delete_student(
            self,
            student_id: UUID4
    ) -> None:
        """Delete a single student by id"""
        await self.repo.delete(student_id)


# Dependency for FastAPI
async def get_student_service(
        session: AsyncSession = Depends(get_tenant_session_dep),
        tenant_id: UUID4 = Depends(get_tenant_id)
):
    return StudentService(session=session, tenant_id=tenant_id)

