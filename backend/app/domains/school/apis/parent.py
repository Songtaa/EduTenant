from typing import Annotated, List

from fastapi import Depends
from pydantic import UUID4
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config.tenant_dependencies import get_tenant_session
from app.domains.school.schemas.parent import (
    ParentCreate,
    ParentUpdate,
    ParentOut,
)
from app.domains.school.services.parent import ParentService, get_parent_service
from app.utils.router import SafeAPIRouter

parent_router = SafeAPIRouter(prefix="/parents")

sessionDep = Annotated[AsyncSession, Depends(get_tenant_session)]



@parent_router.post("", response_model=ParentOut)
async def create_parent(
        school_id: UUID4,
        parent_data: ParentCreate,
        service: ParentService = Depends(get_parent_service),
):
    parent = await service.create_parent(parent_data, school_id)
    return parent


@parent_router.patch("/{parent_id}", response_model=ParentOut)
async def update_parent(
        school_id: UUID4,
        parent_id: UUID4,
        parent_data: ParentUpdate,
        service: ParentService = Depends(get_parent_service),
):
    updated_parent = await service.update_parent(parent_id, parent_data)

    return updated_parent


@parent_router.get("", response_model=List[ParentOut])
async def get_all_parents(
        school_id: UUID4,
        service: ParentService = Depends(get_parent_service),
        skip: int = 0,
        limit: int = 10
):
    return await service.list_parents(skip, limit)


@parent_router.delete("/{parent_id}", status_code=204)
async def delete_parent(
        school_id: UUID4,
        parent_id: UUID4,
        service: ParentService = Depends(get_parent_service),
):
    return await service.delete_parent(parent_id)


