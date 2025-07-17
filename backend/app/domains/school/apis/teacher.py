from typing import Annotated, List

from fastapi import Depends
from pydantic import UUID4
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config.tenant_dependencies import get_tenant_session
from app.domains.school.schemas.teacher import (
    TeacherCreate,
    TeacherUpdate,
    TeacherOut,
)
from app.domains.school.services.teacher import TeacherService, get_teacher_service
from app.utils.router import SafeAPIRouter

teacher_router = SafeAPIRouter(prefix="/teachers")

sessionDep = Annotated[AsyncSession, Depends(get_tenant_session)]



@teacher_router.post("", response_model=TeacherOut)
async def create_teacher(
        school_id: UUID4,
        teacher_data: TeacherCreate,
        service: TeacherService = Depends(get_teacher_service),
):
    teacher = await service.create_teacher(teacher_data, school_id)
    return teacher


@teacher_router.patch("/{teacher_id}", response_model=TeacherOut)
async def update_teacher(
        school_id: UUID4,
        teacher_id: UUID4,
        teacher_data: TeacherUpdate,
        service: TeacherService = Depends(get_teacher_service),
):
    updated_teacher = await service.update_teacher(teacher_id, teacher_data)

    return updated_teacher


@teacher_router.get("", response_model=List[TeacherOut])
async def get_all_teachers(
        school_id: UUID4,
        service: TeacherService = Depends(get_teacher_service),
        skip: int = 0,
        limit: int = 10
):
    return await service.list_teachers(skip, limit)


@teacher_router.delete("/{teacher_id}", status_code=204)
async def delete_teacher(
        school_id: UUID4,
        teacher_id: UUID4,
        service: TeacherService = Depends(get_teacher_service),
):
    return await service.delete_teacher(teacher_id)


