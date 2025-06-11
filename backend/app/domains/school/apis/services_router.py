from typing import Annotated

from app.db.session import get_master_session
from app.domains.school.services.services_service import (
    Service,
    ServiceCreate,
    ServiceUpdate,
)
from app.utils.auth_dep import access_token_bearer
from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

# from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.ext.asyncio.session import AsyncSession

service_router = APIRouter(prefix="/services", tags=["Services"])

sessionDep = Annotated[AsyncSession, Depends(get_master_session)]


@service_router.post("/", response_model=ServiceCreate)
async def create_service(service_data: ServiceCreate, session: sessionDep):
    _service = Service(session)
    service = await _service.create(service_data)
    return service


@service_router.patch("/{service_id}", response_model=ServiceUpdate)
async def update_service(
    service_id: str, service_data: ServiceUpdate, session: sessionDep
):
    _service = Service(session)
    service = await _service.update(service_id, service_data)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@service_router.get("/", response_model=list[ServiceCreate])
async def get_all_services(
    session: sessionDep, user_details=Depends(access_token_bearer)
):
    _service = Service(session)
    return await _service.get_all()


@service_router.delete("/{_id}", status_code=204)
async def delete_service(
    _id: UUID4,
    session: sessionDep,
):
    _service = Service(session)
    return await _service.delete(_id)
