from typing import Annotated

from fastapi import Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.config.tenant_dependencies import get_tenant_session
from app.domains.school.schemas.classes import (
    ClassesOut, ClassesCreate, ClassesUpdate
)
from app.domains.school.services.classes import ClassService, get_class_service
from app.utils.router import SafeAPIRouter

class_router = SafeAPIRouter(prefix="/classes")

sessionDep = Annotated[AsyncSession, Depends(get_tenant_session)]


@class_router.post("", response_model=ClassesOut)
async def create_class(
        school_id: UUID4,
        class_data: ClassesCreate,
        service: ClassService = Depends(get_class_service),
):
    _class = await service.create_class(class_data, school_id)
    return _class


@class_router.patch("/{class_id}", response_model=ClassesOut)
async def update_class(
        school_id: UUID4,
        class_id: UUID4,
        class_data: ClassesUpdate,
        service: ClassService = Depends(get_class_service),
):
    _class = await service.get_class(class_id)
    updated_class = await service.update_class(class_id, class_data)

    return updated_class


@class_router.get("", response_model=list[ClassesOut])
async def get_all_classes(
        school_id: UUID4,
        service: ClassService = Depends(get_class_service),
        skip: int = 0,
        limit: int = 10
):
    return await service.list_classes(skip, limit)


@class_router.delete("/{class_id}", status_code=204)
async def delete_class(
        school_id: UUID4,
        class_id: UUID4,
        service: ClassService = Depends(get_class_service),
):
    return await service.delete_class(class_id)
