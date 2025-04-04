from datetime import timedelta

from app.config.settings import settings
from app.domains.auth.repository.user_repository import UserRepository
from fastapi.responses import JSONResponse
from app.utils.errors import InvalidCredentials
from app.utils.security import Security

from app.domains.auth.schemas.login_schema import UserLoginModel

from sqlmodel.ext.asyncio.session import AsyncSession



class AuthService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)

    async def login_user(self, login_data: UserLoginModel):
        # email = login_data.email
        # password = login_data.password

        user = await self.repository.get_user_by_email(login_data.email)

        if user is not None:
            password_valid = Security.verify_password(
                login_data.password, user.password
            )

            if password_valid:
                access_token = Security.create_access_token(
                    user_data={"email": user.email, "user_uid": str(user.id)}
                )

                refresh_token = Security.create_access_token(
                    user_data={"email": user.email, "user_id": str(user.id)},
                    refresh=True,
                    expiry=timedelta(days=settings.REFRESH_TOKEN_EXPIRY),
                )

                return JSONResponse(
                    content={
                        "message": "Login successful",
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "user": {"email": user.email, "uid": str(user.id)},
                    }
                )

        raise InvalidCredentials()