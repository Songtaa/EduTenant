from typing import Annotated, List

from fastapi import Depends
from pydantic import UUID4
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config.tenant_dependencies import get_tenant_session
from app.domains.school.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentOut,
)
from app.domains.school.services.student import StudentService, get_student_service
from app.utils.router import SafeAPIRouter

student_router = SafeAPIRouter(prefix="/students")

sessionDep = Annotated[AsyncSession, Depends(get_tenant_session)]



@student_router.post("", response_model=StudentOut)
async def create_student(
        school_id: UUID4,
        student_data: StudentCreate,
        service: StudentService = Depends(get_student_service),
):
    student = await service.create_student(student_data, school_id)
    return student


@student_router.patch("/{student_id}", response_model=StudentOut)
async def update_student(
        school_id: UUID4,
        student_id: UUID4,
        student_data: StudentUpdate,
        service: StudentService = Depends(get_student_service),
):
    updated_student = await service.update_student(student_id, student_data)

    return updated_student


@student_router.get("", response_model=List[StudentOut])
async def get_all_students(
        school_id: UUID4,
        service: StudentService = Depends(get_student_service),
        skip: int = 0,
        limit: int = 10
):
    return await service.list_students(skip, limit)


@student_router.delete("/{student_id}", status_code=204)
async def delete_student(
        school_id: UUID4,
        student_id: UUID4,
        service: StudentService = Depends(get_student_service),
):
    return await service.delete_student(student_id)


