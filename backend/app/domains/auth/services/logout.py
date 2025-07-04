from datetime import datetime

from db.session import get_db
from domains.auth.models.refresh_token import RefreshToken
from domains.auth.models.users import User
from fastapi import Depends, HTTPException, Request, Response, status
from jose import JWTError
from sqlalchemy.orm import Session
from utils.security import Security

from .login_service import login_service


class LogoutService:
    async def logout_user(
        self, request: Request, response: Response, db: Session = Depends(get_db)
    ):
        tokens = login_service.get_tokens(request)
        if not tokens["AccessToken"] or not tokens["RefreshToken"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided"
            )

        # Verify the refresh token
        try:
            payload = Security.decode_token(tokens["AccessToken"])
            user_email = payload.get("sub")
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid tokens"
            )

        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to determine logged-in user",
            )

        print("email from payload token: ", user_email)
        # Retrieve the user's refresh token
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        refresh_token = (
            db.query(RefreshToken).filter(RefreshToken.user_id == user.id).first()
        )
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Refresh token not found"
            )

        # Invalidate the token by setting the logged_out_at timestamp
        refresh_token.logged_out_at = datetime.now()
        db.commit()

        # Clear tokens from the cookies
        response.delete_cookie(key="AccessToken")
        response.delete_cookie(key="RefreshToken")

        return {"status": "logged out successfully"}


logoutservice = LogoutService()
