import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

# from jose import JWTError, jwt
import jwt
from app.config.settings import settings
from app.domains.auth.models.users import User
from fastapi import Request, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class Security:
    @staticmethod
    def get_user_by_email(username: str, db: Session):
        user = db.query(User).filter_by(email=username).first()
        if not user:
            return False
        return user

    @staticmethod
    def verify_password(plain_password, hashed_password) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    # function to authenticate user
    @staticmethod
    def authenticate_user(username: str, password: str, db: Session):
        db_user = Security.get_user_by_email(username=username, db=db)
        if not db_user:
            return False
        if not Security.verify_password(password, db_user.password):
            return False
        return db_user

    # function to get hash password
    @staticmethod
    def generate_password_hash(password: str):
        hash = pwd_context.hash(password)
        return hash

    # Generate access token function
    # @staticmethod
    # def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    #     to_encode = data.copy()
    #     if expires_delta:
    #         expire = datetime.now(tz=timezone.utc) + expires_delta
    #     else:
    #         expire = datetime.now(tz=timezone.utc) + timedelta(
    #             minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    #         )
    #     to_encode.update({"exp": expire})
    #     encoded_jwt = jwt.encode(
    #         to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    #     )
    #     return encoded_jwt

    # Generate Access token function
    @staticmethod
    def create_access_token(
        user_data: dict, expiry: timedelta = None, refresh: bool = False
    ):
        payload = {}

        payload["user"] = user_data
        payload["exp"] = datetime.now() + (
            expiry
            if expiry is not None
            else timedelta(seconds=settings.ACCESS_TOKEN_EXPIRY)
        )
        payload["jti"] = str(uuid.uuid4())

        payload["refresh"] = refresh

        token = jwt.encode(
            payload=payload, key=settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

        return token

    # decode token
    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            token_data = jwt.decode(
                jwt=token, key=settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )

            return token_data

        except jwt.PyJWTError:
            # logging(e)
            logging.error("Exception occurred", exc_info=True)
            return None

    # Generate reset password token function
    @staticmethod
    def generate_reset_password_token(expires: int = None):
        if expires is not None:
            # expires = datetime.now(tz=timezone.utc) + expires
            expires = datetime.now(tz=timezone.utc) + expires
        else:
            expires = datetime.now(tz=timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode = {"exp": expires}
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_access_token(request: Request, token: str):
        ## decode the token to get the user id and then fetch the user role
        ## lets check if the cookies for access token is set
        cookie_access_token = request.cookies.get("AccessToken")

        if cookie_access_token is None or cookie_access_token != token:
            raise HTTPException(status_code=401, detail="Access token is invalidated")
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate new access token credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                cookie_access_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            user = User(email=username)
        except jwt.PyJWTError:
            raise credentials_exception
        return user

    # Generate refresh access token function
    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(tz=timezone.utc) + expires_delta
        else:
            expire = datetime.now(tz=timezone.utc) + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    # @staticmethod
    # def decode_token(token: str):
    #     try:
    #         # print("token in decode_token: ", token)
    #         payload = jwt.decode(
    #             token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
    #         )
    #         # print("\npayload in decode_token: ", payload)
    #         return payload
    #     except JWTError:
    #         return None
