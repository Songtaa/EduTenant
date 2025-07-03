from typing import Annotated, AsyncGenerator, List

from app.db.session import db_session_dependency, get_master_session
from fastapi import APIRouter, Depends, status
from pydantic import UUID4
from sqlalchemy.ext.asyncio.session import AsyncSession
from app.utils.auth_dep import AccessTokenBearer

from app.domains.auth.schemas.user_schema import (
    UserCreate,
    UserSchema,
    UserUpdate,
)
from app.domains.auth.services.user_service import UserService

user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)



async def get_master_session_dep() -> AsyncGenerator[AsyncSession, None]:
    async with get_master_session() as session:
        yield session

sessionDep = Annotated[AsyncSession, Depends(get_master_session_dep)]
    
access_token_bearer = Annotated[dict, Depends(AccessTokenBearer())]


@user_router.post(
    "/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED
)
async def create_user_Account(
    user_data: UserCreate, session: sessionDep
):
    user_service = UserService(session)
    new_user = await user_service.create(user_data)

    return new_user


@user_router.get("/users", status_code=200, response_model=List[UserSchema])
async def get_all_users(
    session: sessionDep, user_details:access_token_bearer
) -> List[UserSchema]:
    user_service = UserService(session)
    users = await user_service.get_all()
    return users


@user_router.patch("/{_id}", status_code=200, response_model=UserSchema)
async def update_user(
    _id: UUID4,
    data: UserUpdate,
    session: sessionDep,
):
    _service = UserService(session)
    return await _service.update(_id, data)


@user_router.delete("/{_id}", status_code=204)
async def delete_user(
    _id: UUID4,
    session: sessionDep,
):
    _service = UserService(session)
    return await _service.delete(_id)


# @user_router.post("/login")
# async def login(login_data: UserLogin, session: sessionDep):
#     user_service = UserService(session)

#     return await user_service.login_user(login_data)
