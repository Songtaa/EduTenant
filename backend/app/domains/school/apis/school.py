from typing import Annotated, List, Optional
from uuid import UUID
from fastapi import Response

from app.db.session import get_master_session
from app.domains.school.services.school import (
    SchoolService,
    SchoolCreate,
    SchoolUpdate,
    get_school_service,
)
from app.utils.auth_dep import access_token_bearer
from app.domains.school.schemas.school import SchoolOut
from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import UUID4
from app.utils.dependencies import get_tenant_session
from app.config.tenant_dependencies import get_tenant_id, get_tenant_session

school_router = APIRouter(prefix="/schools", tags=["Schools"])


sessionDep = Annotated[AsyncSession, Depends(get_tenant_session)]


@school_router.get("/", response_model=List[SchoolOut])
async def get_schools(
    service: SchoolService = Depends(get_school_service),
    search_term: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    return await service.list_schools(
        search_term=search_term,
        skip=skip,
        limit=limit
    )
@school_router.post("/", response_model=SchoolOut)
async def create_school(
    school_data: SchoolCreate,
    service: SchoolService = Depends(get_school_service)
)-> SchoolOut:
    return await service.create_school(school_data)


@school_router.patch("/{school_id}", response_model=SchoolUpdate)
async def update_school(
    school_id: UUID4,
    school_data: SchoolUpdate,
    service: SchoolService = Depends(get_school_service)
):
    school = await service.update_school(school_id, school_data)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school






@school_router.delete("/{school_id}", status_code=200)
async def delete_school(
    school_id: UUID,
    service: SchoolService = Depends(get_school_service)
):
    deleted = await service.delete_school(school_id)
    if deleted:
        return {"message": "School deleted successfully."}
    raise HTTPException(status_code=404, detail="School not found")

