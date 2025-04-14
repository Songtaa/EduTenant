from app.crud.base import BaseRepository
from app.domains.auth.models.users import User
from app.domains.auth.schemas.user_account import UserCreate, UserUpdate
import jwt
from datetime import datetime
from app.utils.security import Security # Assuming this is where `create_access_token` is defined
from fastapi import HTTPException, status
from app.utils.errors import InvalidToken


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
