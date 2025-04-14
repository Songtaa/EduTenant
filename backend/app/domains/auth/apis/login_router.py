from typing import Annotated

from fastapi.responses import JSONResponse

from app.db.session import get_master_session
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domains.auth.schemas.login_schema import UserLoginModel
from app.domains.auth.services.login_service import AuthService
from app.utils.errors import UserAlreadyExists, UserNotFound, InvalidCredentials, InvalidToken
from app.domains.auth.repository.login_repository import AuthRepository
from app.utils.auth_dep import RefreshTokenBearer, AccessTokenBearer, RoleChecker
from app.db.redis import add_jti_to_blocklist
from app.utils.auth_dep import get_current_user

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

sessionDep = Annotated[AsyncSession, Depends(get_master_session)]
roleCheck = RoleChecker(['admin', 'user'])


@auth_router.get("/me")
async def get_current_user(user=Depends(get_current_user), _bool= Depends(roleCheck)):
    return user

@auth_router.post("/login")
async def login(login_data: UserLoginModel, session: sessionDep):
    auth_service = AuthService(session)

    return await auth_service.login_user(login_data)



@auth_router.get("/refresh_token")
async def get_new_access_token(
    token_details: dict = Depends(RefreshTokenBearer()), 
    auth_repo: AuthRepository = Depends()
):
    
    new_access_token = await auth_repo.refresh_access_token(token_details)

    
    return JSONResponse(content={"access_token": new_access_token}) 


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "Logged Out Successfully"}, status_code=status.HTTP_200_OK
    )