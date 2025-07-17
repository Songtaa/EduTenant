from typing import Annotated, List

from fastapi import Depends
from pydantic import UUID4
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config.tenant_dependencies import get_tenant_session
from app.domains.school.schemas.programme import (
    ProgrammeCreate,
    ProgrammeUpdate,
    ProgrammeOut,
)
from app.domains.school.services.programme import ProgrammeService, get_programme_service
from app.utils.router import SafeAPIRouter

programme_router = SafeAPIRouter(prefix="/programmes")

sessionDep = Annotated[AsyncSession, Depends(get_tenant_session)]



@programme_router.post("", response_model=ProgrammeOut)
async def create_programme(
        school_id: UUID4,
        programme_data: ProgrammeCreate,
        service: ProgrammeService = Depends(get_programme_service),
):
    programme = await service.create_programme(programme_data, school_id)
    return programme


@programme_router.patch("/{programme_id}", response_model=ProgrammeOut)
async def update_programme(
        school_id: UUID4,
        programme_id: UUID4,
        programme_data: ProgrammeUpdate,
        service: ProgrammeService = Depends(get_programme_service),
):
    updated_programme = await service.update_programme(programme_id, programme_data)

    return updated_programme


@programme_router.get("", response_model=List[ProgrammeOut])
async def get_all_programmes(
        school_id: UUID4,
        service: ProgrammeService = Depends(get_programme_service),
        skip: int = 0,
        limit: int = 10
):
    return await service.list_programmes(skip, limit)


@programme_router.delete("/{programme_id}", status_code=204)
async def delete_programme(
        school_id: UUID4,
        programme_id: UUID4,
        service: ProgrammeService = Depends(get_programme_service),
):
    return await service.delete_programme(programme_id)


