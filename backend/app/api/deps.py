from typing import Optional
from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.errors import AppException
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency for authenticating Bearer JWT tokens and loading the user."""
    if not credentials or not credentials.credentials:
        raise AppException(
            message="Authentication token is required.",
            code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise AppException(
            message="Invalid or expired authentication token.",
            code="INVALID_TOKEN",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AppException(
            message="User associated with token does not exist.",
            code="USER_NOT_FOUND",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_active:
        raise AppException(
            message="User account is inactive.",
            code="ACCOUNT_INACTIVE",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    return user
