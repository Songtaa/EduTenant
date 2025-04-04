from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Annotated, List

from app.domains.auth.schemas.permission import PermissionCreate, PermissionSchema, PermissionUpdate
from app.domains.auth.services.permission import PermissionService
from app.db.session import get_session


router = APIRouter()

sessionDep = Annotated[AsyncSession, Depends(get_session)]

permission_router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
    responses={404: {"description": "Not found"}},
)


@permission_router.post("/", response_model=PermissionSchema)
async def create_permission(permission_data: PermissionCreate, session: sessionDep):
    _service = PermissionService(session)
    return await _service.create(permission_data)


@permission_router.patch("/{permission_id}", response_model=PermissionSchema)
async def update_permission(permission_id: UUID4, permission_data: PermissionUpdate, session: sessionDep):
    _service = PermissionService(session)
    return await _service.update(permission_id, permission_data)


@permission_router.get("/", response_model=List[PermissionSchema])
async def get_all_permissions(session: sessionDep):
    _service = PermissionService(session)
    return await _service.get_all()


@permission_router.get("/{permission_id}", response_model=PermissionSchema)
async def get_permission(permission_id: UUID4, session: sessionDep):
    _service = PermissionService(session)
    return await _service.get_by_id(permission_id)


@permission_router.delete("/{permission_id}", status_code=204)
async def delete_permission(permission_id: UUID4, session: sessionDep):
    _service = PermissionService(session)
    await _service.delete(permission_id)
    return {"message": "Permission deleted successfully"}


@permission_router.get("/role/{role_id}", response_model=List[PermissionSchema])
async def get_permissions_by_role(role_id: UUID4, session: sessionDep):
    _service = PermissionService(session)
    return await _service.get_permissions_by_role(role_id)


@permission_router.get("/user/{user_id}", response_model=List[PermissionSchema])
async def get_permissions_by_user(user_id: UUID4, session: sessionDep):
    _service = PermissionService(session)
    return await _service.get_permissions_by_user(user_id)


@permission_router.post("/role/{role_id}/permission/{permission_id}", response_model=dict)
async def assign_permission_to_role(role_id: UUID4, permission_id: UUID4, session: sessionDep):
    _service = PermissionService(session)
    await _service.assign_permission_to_role(role_id, permission_id)
    return {"message": f"Permission {permission_id} assigned to role {role_id} successfully"}


@permission_router.post("/user/{user_id}/permission/{permission_id}", response_model=dict)
async def assign_permission_to_user(user_id: UUID4, permission_id: UUID4, session: sessionDep):
    _service = PermissionService(session)
    await _service.assign_permission_to_user(user_id, permission_id)
    return {"message": f"Permission {permission_id} assigned to user {user_id} successfully"}



@permission_router.delete("/role/{role_id}/permission/{permission_id}", response_model=dict)
async def remove_permission_from_role(role_id: UUID4, permission_id: UUID4, session: sessionDep):
    _service = PermissionService(session)
    await _service.remove_permission_from_role(role_id, permission_id)
    return {"message": "Permission removed from role successfully"}


@permission_router.delete("/user/{user_id}/permission/{permission_id}", response_model=dict)
async def remove_permission_from_user(user_id: UUID4, permission_id: UUID4, session: sessionDep):
    _service = PermissionService(session)
    await _service.remove_permission_from_user(user_id, permission_id)
    return {"message": "Permission removed from user successfully"}
