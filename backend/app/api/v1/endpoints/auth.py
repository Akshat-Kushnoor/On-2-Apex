from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.errors import AppException
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.profile import StudentProfile
from app.models.user import User
from app.schemas.auth import Token, UserLogin, UserOut, UserRegister

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
    return Token(access_token=token, token_type="bearer")


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
    return Token(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user's account details."""
    return current_user
