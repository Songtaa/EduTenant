from typing import Annotated

from app.db.session import get_master_session
from app.domains.school.services.tenant import (
    TenantService,
    TenantCreate,
    TenantUpdate,
)
from app.utils.auth_dep import access_token_bearer
from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlmodel.ext.asyncio.session import AsyncSession

tenant_router = APIRouter(prefix="/tenants", tags=["Tenants"])

sessionDep = Annotated[AsyncSession, Depends(get_master_session)]


@tenant_router.post("/", response_model=TenantCreate)
async def create_tenant(tenant_data: TenantCreate, session: sessionDep):
    _tenant = TenantService(session)
    tenant = await _tenant.create_tenant(tenant_data)
    return tenant


@tenant_router.patch("/{tenant_id}", response_model=TenantUpdate)
async def update_tenant(
    tenant_id: str, tenant_data: TenantUpdate, session: sessionDep
):
    _tenant = TenantService(session)
    tenant = await _tenant.update_tenant(tenant_id, tenant_data)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@tenant_router.get("/", response_model=list[TenantCreate])
async def get_all_tenants(
    session: sessionDep, user_details=Depends(access_token_bearer)
):
    _tenant = TenantService(session)
    return await _tenant.get_tenant()


@tenant_router.delete("/{_id}", status_code=204)
async def delete_tenant(
    _id: UUID4,
    session: sessionDep
):
    _tenant = TenantService(session)
    return await _tenant.deactivate_tenant(_id)
