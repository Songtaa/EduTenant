from typing import Annotated, Any, List

from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from app.domains.auth.repository.login_repository import TokenBlocklistRepository
# from app.domains.auth.repository.token_blocklist import TokenRepository
from app.domains.auth.services.token import TokenService
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import db_session_dependency
from app.domains.auth.models.users import User
from app.db.redis import token_in_blocklist

# from src.db.redis import token_in_blocklist

from app.domains.auth.services.user_service import UserService
from app.domains.auth.repository.user_repository import UserRepository
from app.utils.security import Security
from app.utils.errors import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission,
    AccountNotVerified,
)

# sessionDep = Annotated[AsyncSession, Depends(get_master_session)]
sessionDep = Annotated[AsyncSession, Depends(db_session_dependency)]


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        token = creds.credentials
        token_data = Security.decode_token(token)

        if not self.token_valid(token):
            raise InvalidToken()

        
        token_repo = TokenBlocklistRepository(request.state.session)
        token_service = TokenService(token_repo)

        if not await token_service.verify_token_not_blocklisted(token_data["jti"]):
            raise InvalidToken()

        self.verify_token_data(token_data)

        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = Security.decode_token(token)

        return token_data is not None

    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()


# async def get_current_user(
#     session: sessionDep,
#     token_details: dict = Depends(AccessTokenBearer()),
    
# ):
#     user_email = token_details["user"]["email"]

#     user_service = UserService(session)

#     user = await user_service.repository.get_user_by_email(user_email)

#     return user

async def get_current_user(
    session: sessionDep,
    token_data: dict = Depends(AccessTokenBearer()),
) -> User:
    tenant = token_data.get("tenant")  # May be None for superusers
    jti = token_data.get("jti")

    blocklist_repo = TokenBlocklistRepository(session)
    if await blocklist_repo.is_token_blocked(jti, tenant):
        raise HTTPException(status_code=401, detail="Token has been revoked")

    user_email = token_data["user"]["email"]
    user_service = UserService(session)
    user = await user_service.repository.get_user_by_email(user_email)

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def SuperuserRequired(current_user: User = Depends(get_current_user)):
    if not getattr(current_user, "is_superuser", False):
        raise HTTPException(status_code=403, detail="Superuser access required")
    return current_user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
        # if not current_user.is_verified:
        #     raise AccountNotVerified()
        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermission()
    

access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()
