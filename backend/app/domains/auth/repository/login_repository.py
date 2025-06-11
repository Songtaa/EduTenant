from app.crud.base import BaseRepository
from app.domains.auth.models.users import User
from app.domains.auth.schemas.user_account import UserCreate, UserUpdate
import jwt
from datetime import datetime
from app.utils.security import Security # Assuming this is where `create_access_token` is defined
from fastapi import HTTPException, status
from app.utils.errors import InvalidToken
from datetime import timedelta
from app.utils.security import Security
from app.domains.auth.repository.token_blocklist import TokenBlocklistRepository
from app.domains.auth.schemas.auth import TokenResponse
from app.config.settings import settings
from app.domains.auth.repository.user_repository import UserRepository
from sqlmodel.ext.asyncio.session import AsyncSession



class CRUDLoggedUser(BaseRepository[User, UserCreate, UserUpdate]):
    pass


# logged_in_users_actions = CRUDLoggedUser(User)


class AuthRepository:
    def __init__(self):
        pass

    async def refresh_access_token(self, token_details: dict):
        expiry_timestamp = token_details["exp"]

        # Check if the refresh token is still valid
        if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
            # Generate a new access token
            new_access_token = Security.create_access_token(user_data=token_details["user"])
            return new_access_token

        # Raise an exception if the token is invalid/expired
        raise InvalidToken


# class AuthService:
#     def __init__(self, session: AsyncSession):
#         self.repository = UserRepository(session)
#         self.blocklist_repo = TokenBlocklistRepository(session)

#     async def refresh_user_token(self, token_data: dict) -> TokenResponse:
#         jti = token_data["jti"]
#         tenant = token_data.get("tenant")
#         user_data = token_data["user"]

#         # Block the used refresh token (revoke)
#         await self.blocklist_repo.add_token_to_blocklist(jti, tenant)

#         # Generate new access + refresh tokens
#         access_token = Security.create_access_token(user_data=user_data)
#         refresh_token = Security.create_access_token(
#             user_data=user_data,
#             refresh=True,
#             expiry=timedelta(days=settings.REFRESH_TOKEN_EXPIRY),
#         )

#         return TokenResponse(
#             access_token=access_token,
#             refresh_token=refresh_token,
#         )
