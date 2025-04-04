from typing import Annotated, Any, List

from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session
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

sessionDep = Annotated[AsyncSession, Depends(get_session)]



class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)

        token = creds.credentials

        token_data = Security.decode_token(token)

        if not self.token_valid(token):
            raise InvalidToken() 

        if await token_in_blocklist(token_data["jti"]):
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


async def get_current_user(
    session: sessionDep,
    token_details: dict = Depends(AccessTokenBearer()),
    
):
    user_email = token_details["user"]["email"]

    user_service = UserService(session)

    user = await user_service.repository.get_user_by_email(user_email)

    return user


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
