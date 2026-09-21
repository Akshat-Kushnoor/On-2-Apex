from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.errors import AppException
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.profile import StudentProfile
from app.models.user import User
from app.schemas.auth import (
    OAuthCallbackRequest,
    OAuthLoginRequest,
    OAuthUrlOut,
    PasswordResetConfirm,
    PasswordResetRequest,
    Token,
    UserLogin,
    UserOut,
    UserRegister,
)
from app.services.oauth_service import oauth_service

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """Registers a new student account, initializes a blank profile, and returns a JWT token."""
    existing_user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing_user:
        raise AppException(
            message="An account with this email address already exists.",
            code="EMAIL_ALREADY_EXISTS",
            status_code=status.HTTP_409_CONFLICT,
        )

    # 1. Create User
    new_user = User(
        email=user_in.email.lower(),
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name.strip(),
        is_active=True,
    )
    db.add(new_user)
    db.flush()  # Populates new_user.id

    # 2. Initialize Empty Student Profile
    initial_profile = StudentProfile(user_id=new_user.id)
    db.add(initial_profile)
    db.commit()
    db.refresh(new_user)

    # 3. Issue Token
    token = create_access_token(subject=new_user.id)
    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(new_user))


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticates credentials and returns a signed JWT access token."""
    user = db.query(User).filter(User.email == credentials.email.lower()).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise AppException(
            message="Incorrect email address or password.",
            code="INVALID_CREDENTIALS",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not user.is_active:
        raise AppException(
            message="This account is currently disabled.",
            code="ACCOUNT_INACTIVE",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    token = create_access_token(subject=user.id)
    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user's account details."""
    return current_user


@router.post("/password-reset-request", status_code=status.HTTP_200_OK)
def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Initiates a password reset request."""
    user = db.query(User).filter(User.email == request.email.lower()).first()
    if not user:
        return {"message": "If the email exists, a password reset link has been sent."}

    token = create_access_token(subject=user.id, expires_delta=timedelta(minutes=15))
    print(f"PASSWORD RESET TOKEN FOR {user.email}: {token}")

    return {
        "message": "If the email exists, a password reset link has been sent.",
        "reset_token": token,
    }


@router.post("/password-reset", status_code=status.HTTP_200_OK)
def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Resets the password using a valid token."""
    payload = decode_access_token(request.token)
    if not payload or "sub" not in payload:
        raise AppException(
            message="Invalid or expired reset token.",
            code="INVALID_TOKEN",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise AppException(
            message="User associated with token not found.",
            code="USER_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    user.hashed_password = hash_password(request.new_password)
    db.commit()
    return {"message": "Password updated successfully."}


@router.get("/oauth/{provider}/url", response_model=OAuthUrlOut)
def get_oauth_url(provider: str, redirect_uri: Optional[str] = Query(default=None)):
    """Returns the OAuth authorization URL for Google or GitHub."""
    return oauth_service.get_oauth_url(provider=provider, redirect_uri=redirect_uri)


@router.post("/oauth/social", response_model=Token)
def login_with_social(request: OAuthLoginRequest, db: Session = Depends(get_db)):
    """Authenticates or registers a user via social provider profile/token."""
    user, token = oauth_service.authenticate_social_user(db=db, request=request)
    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))


@router.post("/google", response_model=Token)
def login_with_google(request: OAuthLoginRequest, db: Session = Depends(get_db)):
    """Convenience endpoint for Google Sign-In."""
    request.provider = "google"
    user, token = oauth_service.authenticate_social_user(db=db, request=request)
    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))


@router.post("/github", response_model=Token)
def login_with_github(request: OAuthLoginRequest, db: Session = Depends(get_db)):
    """Convenience endpoint for GitHub Sign-In."""
    request.provider = "github"
    user, token = oauth_service.authenticate_social_user(db=db, request=request)
    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))


@router.post("/oauth/callback", response_model=Token)
def oauth_callback(payload: OAuthCallbackRequest, db: Session = Depends(get_db)):
    """Exchanges an OAuth authorization code from Google or GitHub for a JWT access token."""
    user, token = oauth_service.exchange_code(
        db=db,
        provider=payload.provider,
        code=payload.code,
        redirect_uri=payload.redirect_uri,
    )
    return Token(access_token=token, token_type="bearer", user=UserOut.model_validate(user))
