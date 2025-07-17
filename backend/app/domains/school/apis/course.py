from typing import Annotated, List

from fastapi import Depends
from pydantic import UUID4
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config.tenant_dependencies import get_tenant_session
from app.domains.school.schemas.course import (
    CourseCreate,
    CourseUpdate,
    CourseOut,
)
from app.domains.school.services.course import CourseService, get_course_service
from app.utils.router import SafeAPIRouter

course_router = SafeAPIRouter(prefix="/courses")

sessionDep = Annotated[AsyncSession, Depends(get_tenant_session)]



@course_router.post("", response_model=CourseOut)
async def create_course(
        school_id: UUID4,
        course_data: CourseCreate,
        service: CourseService = Depends(get_course_service),
):
    course = await service.create_course(course_data, school_id)
    return course


@course_router.patch("/{course_id}", response_model=CourseOut)
async def update_course(
        school_id: UUID4,
        course_id: UUID4,
        course_data: CourseUpdate,
        service: CourseService = Depends(get_course_service),
):
    updated_course = await service.update_course(course_id, course_data)

    return updated_course


@course_router.get("", response_model=List[CourseOut])
async def get_all_courses(
        school_id: UUID4,
        service: CourseService = Depends(get_course_service),
        skip: int = 0,
        limit: int = 10
):
    return await service.list_courses(skip, limit)


@course_router.delete("/{course_id}", status_code=204)
async def delete_course(
        school_id: UUID4,
        course_id: UUID4,
        service: CourseService = Depends(get_course_service),
):
    return await service.delete_course(course_id)


