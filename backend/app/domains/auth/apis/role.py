from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Annotated, List

from app.domains.auth.repository.role import RoleRepository
from app.domains.auth.schemas.role import RoleCreate, RoleSchema, RoleUpdate
from app.domains.auth.services.role import RoleService
from app.db.session import get_session


router = APIRouter()

sessionDep = Annotated[AsyncSession, Depends(get_session)]

role_router = APIRouter(
    prefix="/role",
    tags=["role"],
    responses={404: {"description": "Not found"}},
)


@role_router.post("/", response_model=RoleSchema)
async def create_role(role_data: RoleCreate, session: sessionDep):
    _service = RoleService(session)
    role = await _service.create(role_data)
    return role


@role_router.patch("/{role_id}", response_model=RoleSchema)
async def update_role(role_id: UUID4, role_data: RoleUpdate, session: sessionDep):
    _service = RoleService(session)
    role = await _service.update(role_id, role_data)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@role_router.get("/", response_model=List[RoleSchema])
async def get_all_roles(session: sessionDep):
    _service = RoleService(session)
    return await _service.get_all()


@role_router.delete("/{role_id}", status_code=204)
async def delete_role(role_id: UUID4, session: sessionDep):
    _service = RoleService(session)
    return await _service.delete(role_id)


@role_router.get("/user/{user_id}", response_model=List[RoleSchema])
async def get_roles_by_user(user_id: UUID4, session: sessionDep):
    _service = RoleService(session)
    roles = await _service.get_roles_by_user(user_id)
    return roles



@role_router.post("/user/{user_id}/role/{role_id}", response_model=dict)
async def assign_role_to_user(user_id: UUID4, role_id: UUID4, session: sessionDep):
    _service = RoleService(session)
    result = await _service.assign_role_to_user(user_id, role_id)
    return result



@role_router.delete("/user/{user_id}/role/{role_id}", response_model=dict)
async def remove_role_from_user(user_id: UUID4, role_id: UUID4, session: sessionDep):
    _service = RoleService(session)
    result = await _service.remove_role_from_user(user_id, role_id)
    return result