from typing import Annotated, AsyncGenerator, List

from app.db.session import get_master_session
# from app.utils.dependencies import get_master_engine
from app.domains.school.services.tenant import (
    TenantService,
    TenantCreate,
    TenantUpdate,
    TenantRead,
    TenantSchema,
)
from app.utils.auth_dep import access_token_bearer
from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlmodel.ext.asyncio.session import AsyncSession

tenant_management_router = APIRouter(prefix="/tenants", tags=["Tenants management"])

async def get_master_session_dep() -> AsyncGenerator[AsyncSession, None]:
    async with get_master_session() as session:
        yield session

sessionDep = Annotated[AsyncSession, Depends(get_master_session_dep)]


@tenant_management_router.post("/", response_model=TenantCreate)
async def create_tenant(tenant_data: TenantCreate, session: sessionDep,
                        ):
    _tenant = TenantService(session)
    tenant = await _tenant.create_tenant(tenant_data)
    return tenant


@tenant_management_router.patch("/{tenant_id}", response_model=TenantSchema)
async def update_tenant(
    tenant_id: str, tenant_data: TenantUpdate, session: sessionDep
):
    _tenant = TenantService(session)
    tenant = await _tenant.update_tenant(tenant_id, tenant_data)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@tenant_management_router.get("/", response_model=list[TenantSchema])
async def get_all_tenants(
    session: sessionDep, user_details=Depends(access_token_bearer)
) -> List[TenantSchema]:
    _tenant = TenantService(session)
    return await _tenant.get_all()


@tenant_management_router.delete("/{_id}", status_code=204)
async def delete_tenant(
    _id: UUID4,
    session: sessionDep
):
    _tenant = TenantService(session)
    return await _tenant.deactivate_tenant(_id)
