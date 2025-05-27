from datetime import datetime, timedelta, timezone

from app.config.settings import settings
from app.domains.auth.repository.user_repository import UserRepository
from fastapi.responses import JSONResponse
from app.utils.errors import InvalidCredentials
from app.utils.security import Security

from app.domains.auth.schemas.login_schema import UserLoginModel

from app.domains.auth.repository.token_blocklist import  TokenBlocklistRepository
from app.domains.auth.schemas.auth import TokenResponse
from sqlmodel.ext.asyncio.session import AsyncSession



class AuthService:
    def __init__(self, session):
        self.repository = UserRepository(session)
        self.blocklist_repo = TokenBlocklistRepository(session)


    async def login_user(self, login_data: UserLoginModel, tenant: str | None = None):
        user = await self.repository.get_user_by_email(login_data.email)

        if user is None:
            raise InvalidCredentials()

        if not Security.verify_password(login_data.password, user.password):
            raise InvalidCredentials()

        # Superuser has no tenant
        is_superuser = getattr(user, "is_superuser", False)
        tenant_claim = None if is_superuser else tenant

        user_data = {
            "email": user.email,
            "user_uid": str(user.id),
            "superuser": is_superuser,
            "tenant": tenant_claim,
        }

        access_token = Security.create_access_token(user_data=user_data)
        refresh_token = Security.create_access_token(
            user_data=user_data,
            refresh=True,
            expiry=timedelta(days=settings.REFRESH_TOKEN_EXPIRY),
        )

        return JSONResponse(
            content={
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "email": user.email,
                    "uid": str(user.id),
                    "superuser": is_superuser,
                    "tenant": tenant_claim,
                },
            }
        )

    async def refresh_user_token(self, token_data: dict) -> TokenResponse:
        jti = token_data["jti"]
        tenant = token_data.get("tenant")
        expires_at = datetime.fromtimestamp(token_data["exp"]) 

        user_data = {
            "email": token_data["email"],
            "user_id": token_data["sub"],  
            "tenant": tenant,
        }

        
        await self.blocklist_repo.add_token_to_blocklist(
            jti=jti,
            expires_at=expires_at,
            user_id=user_data["user_id"],
            tenant=tenant
        )

        # Generate new access + refresh tokens
        access_token = Security.create_access_token(user_data=user_data)
        refresh_token = Security.create_access_token(
            user_data=user_data,
            refresh=True,
            expiry=timedelta(days=settings.REFRESH_TOKEN_EXPIRY),
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    


    # async def login_user(self, login_data: UserLoginModel, tenant: str | None = None):
    #     user = await self.repository.get_user_by_email(login_data.email)

    #     if user:
    #         password_valid = Security.verify_password(
    #             login_data.password, user.password
    #         )
    #         if password_valid:
    #             payload = {
    #                 "email": user.email,
    #                 "user_id": str(user.id),
    #                 "tenant": tenant
    #             }

    #             access_token = Security.create_access_token(
    #                 user_data=payload
    #             )

    #             refresh_token = Security.create_access_token(
    #                 user_data=payload,
    #                 refresh=True,
    #                 expiry=timedelta(days=settings.REFRESH_TOKEN_EXPIRY)
    #             )

    #             return JSONResponse(
    #                 content={
    #                     "message": "Login successful",
    #                     "access_token": access_token,
    #                     "refresh_token": refresh_token,
    #                     "user": {"email": user.email, "uid": str(user.id)},
    #                     "tenant" : tenant
    #                 }
    #             )

    #     raise InvalidCredentials()