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

    @staticmethod
    def create_access_token(
        user_data: dict,
        expiry: timedelta = None,
        refresh: bool = False
    ) -> str:
        """
        Create a JWT token with tenant info.
        """
        jti = str(uuid.uuid4())
        now = datetime.now(tz=timezone.utc)

        token_expiry = now + (expiry or timedelta(seconds=settings.ACCESS_TOKEN_EXPIRY))

        payload = {
            "sub": str(user_data.get("user_id")),
            "email": user_data.get("email"),
            "tenant": user_data.get("tenant"),
            "jti": jti,
            "refresh": refresh,
            "exp": token_expiry,
        }

        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    # decode token
    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            return jwt.decode(
                token,
                key=settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            logging.error("Token decode failed", exc_info=True)
            return None

    # Generate reset password token function
    @staticmethod
    def generate_reset_password_token(expires: timedelta = None) -> str:
        exp = datetime.now(tz=timezone.utc) + (expires or timedelta(minutes=15))
        return jwt.encode({"exp": exp}, settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)

    @staticmethod
    def verify_access_token(request: Request, token: str):
        cookie_access_token = request.cookies.get("AccessToken")
        if cookie_access_token is None or cookie_access_token != token:
            raise HTTPException(status_code=401, detail="Access token is invalidated")
        try:
            payload = jwt.decode(
                cookie_access_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            return User(email=payload.get("email"))
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

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