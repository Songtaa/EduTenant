from typing import Annotated

from fastapi.responses import JSONResponse

from app.db.session import db_session_dependency
from fastapi import APIRouter, Depends, status, Request
from app.domains.auth.repository.token_blocklist import TokenBlocklistRepository
from app.domains.auth.schemas.auth import TokenData, TokenResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domains.auth.schemas.login_schema import UserLoginModel
from app.domains.auth.services.login_service import AuthService
from app.utils.errors import UserAlreadyExists, UserNotFound, InvalidCredentials, InvalidToken
from app.domains.auth.services.login_service import AuthService
from app.utils.auth_dep import RefreshTokenBearer, AccessTokenBearer, RoleChecker
# from app.db.redis import add_jti_to_blocklist
from app.utils.auth_dep import get_current_user


auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

# sessionDep = Annotated[AsyncSession, Depends(get_master_session)]
# sessionDep = Annotated[AsyncSession, Depends(master_session_dependency)]
sessionDep = Annotated[AsyncSession, Depends(db_session_dependency)]

roleCheck = RoleChecker(['admin', 'user'])


@auth_router.get("/me")
async def get_current_user(user=Depends(get_current_user), _bool= Depends(roleCheck)):
    return user


@auth_router.post("/login")
async def login(
    login_data: UserLoginModel,
    request: Request,
    session: sessionDep,
):
    tenant = request.headers.get("X-Tenant-ID") or request.url.hostname.split(".")[0]

    auth_service = AuthService(session)
    response = await auth_service.login_user(login_data, tenant=tenant)

    return response




# @auth_router.get("/refresh_token")
# async def get_new_access_token(
#     token_details: dict = Depends(RefreshTokenBearer()), 
#     auth_repo: AuthRepository = Depends()
# ):
    
#     new_access_token = await auth_repo.refresh_access_token(token_details)

    
#     return JSONResponse(content={"access_token": new_access_token})

@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    session: sessionDep,
    token_data: dict = Depends(RefreshTokenBearer())
    
):
    auth_service = AuthService(session)
    tokens = await auth_service.refresh_user_token(token_data)
    return tokens



# @auth_router.get("/logout")
# async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
#     jti = token_details["jti"]

#     await add_jti_to_blocklist(jti)

#     return JSONResponse(
#         content={"message": "Logged Out Successfully"}, status_code=status.HTTP_200_OK
# )

@auth_router.post("/logout")
async def logout(
    session: sessionDep,
    token_data: dict = Depends(AccessTokenBearer()),
    
):
    jti = token_data["jti"]
    tenant = token_data.get("tenant")

    blocklist_repo = TokenBlocklistRepository(session)
    await blocklist_repo.add_token_to_blocklist(jti, tenant)

    return {"message": "Logout successful"}